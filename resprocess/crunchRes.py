#does not contain indexing of ontology and paragraph/sentence - not essential
#only supports one type of concepts at a time at the moment
#be careful of bulk_create - bulk_size is not supported until Django 1.5 and mySQL has a limit of insertions which is >10,000, but still limited

from main.models import *
#from nltk.tokenize import sent_tokenize
import sys
import cPickle as pickle
import zlib
from scipy.sparse import coo_matrix, csr_matrix, vstack
from scipy import int16
from numpy import array
import math
from time import time
import traceback
from decimal import *
from cleanupRes import cleanupRes
import re
import celery
from celery.result import AsyncResult as celery_result
from threading import Lock
from django.db import connection
from django.core.files.storage import default_storage
import uuid
from django.core.cache import cache

'''pickle and compress obj'''
def pickle_zdumps(obj):
	return zlib.compress(pickle.dumps(obj,pickle.HIGHEST_PROTOCOL),9)

'''unpickle and decompress obj'''
def pickle_zloads(zstr):
	return pickle.loads(zlib.decompress(zstr))
	
'''sets object in chunks to cache'''
def get_chunked_from_cache(cache_key, num_chunks):
	allChunksAvailable = all([(cache_key + '-%s' % i in cache) for i in range(num_chunks)])
	if allChunksAvailable:
		chunksCombined = ''.join([cache.get(cache_key + '-%s' % i) for i in range(num_chunks)])
		return chunksCombined
	else:
		return False  

'''gets chunked object from cache'''
def set_chunked_to_cache(cache_key, obj, num_chunks):
	chunkSize = int(math.ceil(float(len(obj))/float(num_chunks)))
	obj_chunked = [obj[i:i+chunkSize] for i in range(0, len(obj), chunkSize)]
	for i, chunk in enumerate(obj_chunked):
		cache.set(cache_key + '-%s' % i, chunk, 0)
	return
		

'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Gets cache generation number for user. 
Generation number if used for versioning cached contents. 
It is incremented every time the user's underlying data, e.g. big_A, changes, such as when a resource is added or deleted.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''		
def get_user_generation(user_ID):
	cache_key = 'gen' + str(user_ID)
	generation = cache.get(cache_key)
	if not generation:
		generation = 1
		cache.set(cache_key, generation, 0)
	return generation

'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Gets term_set from concept object 
Note: in future, should expire if ontology gets added to domain
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''		
def get_concept_termList(domain_ID):
	cache_key = 'concept_termList_%s' % str(domain_ID)
	x = get_chunked_from_cache(cache_key, 10)
	if x:
		(tot_concepts, concept_IDs, term_lists) = pickle_zloads(x)
	else:
		target_concepts = Concept.objects.filter(ontology__domain__id=domain_ID).prefetch_related('term_set')
		tot_concepts = target_concepts.count()
		concept_IDs = []
		term_lists = []
		for con in target_concepts:
			concept_IDs.append(con.id)
			term_objs = con.term_set.all()
			term_list = []
			for term in term_objs:
				term_list.append(term.name)
			term_lists.append(term_list)
		y = pickle_zdumps((tot_concepts, concept_IDs, term_lists))
		set_chunked_to_cache(cache_key, y, 10)
	return (tot_concepts, concept_IDs, term_lists)
	
'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
cruncRes function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''		
@celery.task
def crunchRes(resource_ID,domain_ID,user_ID):
	if celery_result(celery.current_task.request.id).state == 'SUCCESS':
		return
	else:
		success = False
		try:
			print "***starting crunchRes: resourceID %s, domainID %s, userID %s***" % (resource_ID,domain_ID,user_ID)
			celery.current_task.update_state(state='CONSTRUCT_MATRIX', meta={'percent_done': 0})
			getcontext().prec = 10 #sets the precision points for all Decimal objects used in this script
			#find all the paragraph subresources that script.py has created under resource
			start = time()
			target_paragraphs = Subresource.objects.filter(containing_resource_id=resource_ID).only('content')
			print "    getting subresource contents..." + str(time()-start) + " seconds"
			#get all concept objects with associated terms prefetched
			start = time()
			(tot_concepts, concept_IDs, term_lists) = get_concept_termList(domain_ID)
			print "    loading concepts and term lists..." + str(time()-start) + " seconds"
			
			'''#create sentences from target_paragraphs
			start = time()
			sentences = []
			sentences_indexofparagraph = []
			tot_para = 0
			tot_sent = 0
			for para_num, target_paragraph in enumerate(target_paragraphs):
				#find all sentence in this paragraph
				tokenized_sentences = sent_tokenize(target_paragraph.content.rstrip())
				sentences.extend(tokenized_sentences)
				sentences_indexofparagraph.extend([para_num]*len(tokenized_sentences))
				tot_sent = tot_sent + len(tokenized_sentences)
				tot_para = tot_para + 1
			print "    creating sentences..." + str(time()-start) + " seconds"'''
			tot_para = len(target_paragraphs)
			
			start = time()
			#second go through each concept/term, find them in subresources, and process into matrix
			tc = 0
			j = 0
			row = []
			col = []
			data = []
			# initialize list of empty lists for storing concepts contained in each paragraph
			para_conceptIDs_contained = [[] for i in range(tot_para)]
			for i, con_ID in enumerate(concept_IDs):
				term_list = term_lists[i]
				#wordcount_in_paragraphs = [0] * tot_para
				terms_regex = [r"\b"+re.escape(term.lower())+r"\b" for term in term_list]
				search_pattern = re.compile("|".join(terms_regex))
				'''for sent_num, sentence in enumerate(sentences):
					wordcount = len(search_pattern.findall(sentence.lower()))
					if wordcount > 0: #only go ahead if search_pattern is in the sentence
						row.append(sent_num)
						col.append(tc)
						data.append(wordcount)
						wordcount_in_paragraphs[sentences_indexofparagraph[sent_num]] += wordcount
				for para_num in range(tot_para):
					wordcount_in_p = wordcount_in_paragraphs[para_num]
					if wordcount_in_p > 0:
						para_conceptIDs_contained[para_num].append(con_ID)'''
				for para_num, paragraph in enumerate(target_paragraphs):
					wordcount = len(search_pattern.findall(paragraph.content.lower()))
					if wordcount > 0: #only go ahead if search_pattern is in the paragraph
						row.append(para_num)
						col.append(tc)
						data.append(wordcount)
						para_conceptIDs_contained[para_num].append(con_ID)
				if tc*10/tot_concepts > j:
					percent_done = tc*10/tot_concepts*10
					# update celery task progress, but not too often as this can dramatically increase processing time
					celery.current_task.update_state(state='CONSTRUCT_MATRIX', meta={'percent_done': percent_done})
					#print str(percent_done) + "%",
					#sys.stdout.flush()
					j=j+1
				tc = tc + 1
			print "    constructing raw matrix..." + str(time()-start) + " seconds"
			
			# update concepts_contained fields for all subresource objects
			start = time()
			for para_num in range(tot_para):
				if len(para_conceptIDs_contained[para_num]) > 0:
					target_paragraphs[para_num].concepts_contained.add(*para_conceptIDs_contained[para_num])
			print "    tagging all subresources with contained concepts..." + str(time()-start) + " seconds"
			
			#create target_A matrix
			#target_A = coo_matrix((array(data),(array(row),array(col))),shape=(tot_sent,tot_concepts),dtype=int16)
			target_A = coo_matrix((array(data),(array(row),array(col))),shape=(tot_para,tot_concepts),dtype=int16)
			
			MFS = []
			
			#now convert target_A into a scipy csr_matrix (sparse matrix)
			start = time()
			target_A = target_A.tocsr()
			uid_filename = uuid.uuid4().hex
			path = 'matrices/rawA/%s.pkl' % uid_filename
			MFS.append(MatrixFileSystem(resource_id=resource_ID, domain_id=domain_ID, type='rawA', path=path))
			file = default_storage.open(path,'wb')
			file.write(pickle_zdumps(target_A))
			file.close()

			#calculate AtA for target_A
			AtA = target_A.T * target_A
			uid_filename = uuid.uuid4().hex
			path = 'matrices/AtA/%s.pkl' % uid_filename
			MFS.append(MatrixFileSystem(resource_id=resource_ID, domain_id=domain_ID, type='AtA', path=path))
			file = default_storage.open(path,'wb')
			file.write(pickle_zdumps(AtA))
			file.close()
			
			#calculate covariance matrix covA for target_A
			raw_A = target_A.astype(float)
			mean_vector = csr_matrix(raw_A.mean(axis=0))
			norm_A = raw_A - csr_matrix([1]*raw_A.shape[0]).T * mean_vector
			norm_A = norm_A.tocsr()
			covariance_matrix = (norm_A.T * norm_A) / raw_A.shape[0]
			uid_name = uuid.uuid4().hex
			path = 'matrices/covA/%s.pkl' % uid_filename
			MFS.append(MatrixFileSystem(resource_id=resource_ID, domain_id=domain_ID, type='covA', path=path))
			file = default_storage.open(path,'wb')
			sample_size = raw_A.shape[0]
			covariance_matrix_tuple = (covariance_matrix, sample_size)
			file.write(pickle_zdumps(covariance_matrix_tuple)) # file stores the a tuple with covariance_matrix and sample_size
			file.close()
			
			MFS_temp = MatrixFileSystem.objects.bulk_create(MFS)
			del MFS_temp
			del MFS
			print "    manipulating matrix and saving to S3..." + str(time()-start) + " seconds"
			
			get_user_generation(user_ID)
			cache.incr('gen' + str(user_ID))
			print "    cache generation number for user incremented."
			success = True
			#print "number of SQL queries made:", len(connection.queries)
		except Exception, e:
			print "failed. exception: "+str(e)
			traceback.print_exc()
			print "\n cleaning up resources..."		
			queued_task = cleanupRes(resource_ID,domain_ID,user_ID)		
			print "resources cleaned. please restart process"
		
		QueuedResProcessTask.objects.get(taskID=celery.current_task.request.id).delete()
		return success
