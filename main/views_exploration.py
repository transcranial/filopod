from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import redirect
from django.http import HttpResponse
import itertools
import math
import simplejson as json
from main.models import *
import celery
from nltk.tokenize import sent_tokenize
import re
import cPickle as pickle
import zlib
import numpy
from time import time
import traceback
from django.core.paginator import Paginator
from django.db import connection
from django.core.files.storage import default_storage
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
		return None  

'''gets chunked object from cache'''
def set_chunked_to_cache(cache_key, obj, num_chunks):
	chunkSize = int(math.ceil(float(len(obj))/float(num_chunks)))
	obj_chunked = [obj[i:i+chunkSize] for i in range(0, len(obj), chunkSize)]
	for i, chunk in enumerate(obj_chunked):
		cache.set(cache_key + '-%s' % i, chunk, 0)
	return

'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Resource Exploration view
requires user to be logged in
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''		
def exploration(request):
    if request.user.is_authenticated():
		return render_to_response('tools/exploration.html', RequestContext(request))
    else:
		return redirect('/accounts/login')
		
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
Gets user's big_A matrix from cache. If not present, calculate big_A in real-time.
For distributional frequency, AtA matrices of all resources held by user is summed.
For covariance, a weighted average of covA matrices is calculated.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''	
@celery.task
def get_user_Big_A(user_ID, domain_ID, type):
	generation = get_user_generation(user_ID)
	cache_key = 'gen-%s-bigA_%s_%s_%s' % (str(generation), str(user_ID), str(domain_ID), type)
	x = get_chunked_from_cache(cache_key, 100)
	if x is not None:
		big_A = pickle_zloads(x)
	else: # using if not big_A raises error due to numpy.__nonzero__ system
		if type == 'freq':
			matrices = MatrixFiles.objects.filter(user__id=user_ID).filter(type='AtA')
			if len(matrices) > 0:
				for i, matrix in enumerate(matrices):					
					tempdata = get_chunked_from_cache(matrix.path, 100)
					if not tempdata:
						file = default_storage.open(matrix.path,'rb')
						tempdata = file.read()
						file.close()
						set_chunked_to_cache(matrix.path, tempdata, 100)
					if i == 0:
						big_A = pickle_zloads(tempdata)
					else:
						big_A = big_A + pickle_zloads(tempdata)
			else:
				big_A = None
		elif type == 'cov':
			matrices = MatrixFiles.objects.filter(user__id=user_ID).filter(type='covA')
			if len(matrices) > 0:
				for i, matrix in enumerate(matrices):
					tempdata = get_chunked_from_cache(matrix.path, 100)
					if not tempdata:
						file = default_storage.open(matrix.path,'rb')
						tempdata = file.read()
						file.close()						
						set_chunked_to_cache(matrix.path, tempdata, 100)
					if i == 0:
						(covA, sample_size) = pickle_zloads(tempdata)
						big_A = covA
						tot_sample_size = sample_size
					else:
						(covA, sample_size) = pickle_zloads(tempdata)
						big_A = (big_A * tot_sample_size + covA * sample_size) / (tot_sample_size + sample_size)
						tot_sample_size = tot_sample_size + sample_size
			else:
				big_A = None
		set_chunked_to_cache(cache_key, pickle_zdumps(big_A), 100)
	return big_A

'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Gets domain ID from domain name
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
def get_domain_ID(domain_name):
	cache_key = 'domainID_' + domain_name
	domain_ID = cache.get(cache_key)
	if not domain_ID:
		domain_ID = Domain.objects.get(name=domain_name).id
		cache.set(cache_key, domain_ID, 0)
	return domain_ID
	
'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Gets concept IDs list from cache. If not present, make query.
Note: in future, should expire if ontology gets added to domain
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''		
def get_domain_concept_IDs(domain_ID):
	cache_key = 'conceptIDs_%s' % str(domain_ID)
	concept_IDs = cache.get(cache_key)
	if not concept_IDs:
		concept_IDs = Concept.objects.filter(ontology__domain__id=domain_ID).values_list('id',flat=True) 
		cache.set(cache_key, concept_IDs, 0)
	return concept_IDs

'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Get Concept types
called via ajax to get concept types for a domain
Note: in future, should expire if ontology gets added to domain
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''		
def get_concept_types_from_code(domain_ID, concept_type_code):
	cache_key = 'conceptTypesSelected_%s_%s' % (str(domain_ID), concept_type_code)
	conceptTypesSelected = cache.get(cache_key)
	if not conceptTypesSelected:
		conceptTypesSelected = []
		conceptTypes = list(set(Concept.objects.filter(ontology__domain__id=domain_ID).values_list('type',flat=True)))
		for i in range(len(concept_type_code)):
			if concept_type_code[i] == '1':
				conceptTypesSelected.append(conceptTypes[i])
		cache.set(cache_key, conceptTypesSelected, 0)
	return conceptTypesSelected
	
'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Gets concept IDs list from cache, filtered by selected concept types. If not present, make query.
Note: in future, should expire if ontology gets added to domain
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''		
def get_domain_concept_IDs_byConceptType(domain_ID, concept_type_code):
	cache_key = 'conceptIDsByConceptTypes_%s_%s' % (str(domain_ID), concept_type_code)
	concept_IDs_byConceptTypes = cache.get(cache_key)
	if not concept_IDs_byConceptTypes:
		conceptTypesSelected = get_concept_types_from_code(domain_ID, concept_type_code)
		concept_IDs_byConceptTypes = Concept.objects.filter(ontology__domain__id=domain_ID, type__in=conceptTypesSelected).values_list('id',flat=True) 
		cache.set(cache_key, list(concept_IDs_byConceptTypes), 0)
	return concept_IDs_byConceptTypes
	
'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Get Concept types
called via ajax to get concept types for a domain
Note: in future, should expire if ontology gets added to domain
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''		
def get_concept_types(request):
	if request.is_ajax():
		try:
			domain_name = request.GET.get('domain_name', '')
			domain_ID = get_domain_ID(domain_name)
			cache_key = 'conceptTypes_json_' + str(domain_ID)
			data = cache.get(cache_key)
			if not data:
				concept_IDs = get_domain_concept_IDs(domain_ID)
				conceptTypes = list(set(Concept.objects.filter(id__in=concept_IDs).values_list('type',flat=True)))
				data = json.dumps({'conceptTypes': conceptTypes})
				cache.set(cache_key, data, 0)
		except Exception as inst:
			print inst
			traceback.print_exc()
	else:
		data = 'fail'
	mimetype = 'application/json'
	return HttpResponse(data, mimetype)
		
'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Gets id of concepts with links
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''	
def get_conceptsWithLinks_IDs(user_ID, domain_ID):
	generation = get_user_generation(user_ID)
	cache_key = 'gen-%s-conWithLinks_%s_%s' % (str(generation), str(user_ID), str(domain_ID))
	conceptsWithLinks = cache.get(cache_key)
	if not conceptsWithLinks:
		concept_IDs = list(get_domain_concept_IDs(domain_ID))
		big_A_freq = get_user_Big_A(user_ID, domain_ID, 'freq')
		if big_A_freq is not None:
			nz_indices = big_A_freq.diagonal().nonzero()[0].astype('int').tolist()
			conceptsWithLinks = [concept_IDs[i] for i in nz_indices]
		else:
			conceptsWithLinks = []
		cache.set(cache_key, conceptsWithLinks, 0)
	return conceptsWithLinks

'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
selection autocomplete
called via ajax by concept selection search bar
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''	
def selection_autocomplete(request):
	if request.is_ajax():
		try:
			start = time()
			q = request.GET.get('query', '')
			domain_name = request.GET.get('domain_name', '')
			domain_ID = get_domain_ID(domain_name)
			user_ID = request.user.id
			generation = get_user_generation(user_ID)
			cache_key = 'gen-%s-autocomp_%s_%s_%s' % (str(generation), str(user_ID), str(domain_ID), q.replace(' ','%20'))
			data = cache.get(cache_key)
			if not data:			
				conceptsWithLinks = get_conceptsWithLinks_IDs(user_ID, domain_ID)
				terms = Term.objects.filter(name__icontains = q).select_related('concept__name')
				concepts = []
				suggestions = []
				idnum = []
				for term in terms:
					if len(concepts) == 20:
						break
					if term.concept_id in conceptsWithLinks and term.concept.name not in concepts:
						concepts.append(term.concept.name)
						#suggestions.append(term.name + '<br>(concept name: ' + term.concept.name + ')')
						suggestions.append(term.name)
				data = json.dumps({'query': q, 'suggestions': suggestions, 'data': concepts})
				cache.set(cache_key, data, 0)
			print "time to retrieve autocomplete data: " + str(time()-start) + " seconds"
		except Exception as inst:
			print inst
			traceback.print_exc()
	else:
		data = 'fail'
	#print "number of SQL queries made:", len(connection.queries)
	mimetype = 'application/json'
	return HttpResponse(data, mimetype)

	'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Gets data for displaying network graph
called via ajax by graph button in selection panel
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''		
def network_graph_data(request):
	if request.is_ajax():
		try:
			start = time()
			method = request.GET.get('method', '')
			node_number = int(request.GET.get('node_number', '0'))
			concepts = request.GET.getlist('concepts[]')
			domain_name = request.GET.get('domain_name', '')
			domain_ID = get_domain_ID(domain_name)
			concept_type_code = request.GET.get('concept_type', '')
			user_ID = request.user.id
			
			concept_IDs = list(get_domain_concept_IDs(domain_ID))
			big_A = get_user_Big_A(user_ID, domain_ID, method)
			if big_A is None:
				data = {}
			else:
				core_nodes_index = []
				core_nodes_name = []
				core_nodes_terms = []
				core_nodes_terms_all = []
				core_links_source = []
				core_links_target = []
				core_links_value = []
				if len(concepts) == 1:
					con = Concept.objects.get(name=concepts[0])
					nodeIndex = con.id	
					core_nodes_index.append(nodeIndex)
					core_nodes_name = concepts
					terms = [];
					term_set = con.term_set.values_list('name',flat=True)
					for term_i in term_set:
						if len(terms) > 5:
							terms.append('(plus additional terms...)')
							break
						else:
							terms.append(term_i)
					core_nodes_terms.append(terms)
					for term_i in term_set:					
						core_nodes_terms_all.append(term_i)
				elif len(concepts) > 1:
					for item in concepts:
						con = Concept.objects.get(name=item)
						nodeIndex = con.id	
						core_nodes_index.append(nodeIndex)
						core_nodes_name.append(item)
						terms = [];
						term_set = con.term_set.values_list('name',flat=True)
						for term_i in term_set:
							if len(terms) > 5:
								terms.append('(plus additional terms...)')
								break
							else:
								terms.append(term_i)
						core_nodes_terms.append(terms)
						for term_i in term_set:					
							core_nodes_terms_all.append(term_i)
					for s, t in itertools.combinations(core_nodes_index, 2):
						core_links_source.append(s)
						core_links_target.append(t)
						if method == 'freq': # big_A are freqs - calculate conditional probability from frequencies
							linkStrength1 = big_A[concept_IDs.index(s), concept_IDs.index(t)].astype('float') / big_A[concept_IDs.index(s), concept_IDs.index(s)].astype('float')
							linkStrength2 = big_A[concept_IDs.index(t), concept_IDs.index(s)].astype('float') / big_A[concept_IDs.index(t), concept_IDs.index(t)].astype('float')
						elif method == 'cov': # big_A are covariances - calculate Pearson correlation coefficient from covariance matrix
							cov_XY1 = big_A[concept_IDs.index(s), concept_IDs.index(t)].astype('float')
							stddev_X1 = numpy.sqrt(big_A[concept_IDs.index(s), concept_IDs.index(s)].astype('float'))
							stddev_Y1 = numpy.sqrt(big_A[concept_IDs.index(t), concept_IDs.index(t)].astype('float'))
							linkStrength1 = cov_XY1 / (stddev_X1 * stddev_Y1)
							cov_XY2 = big_A[concept_IDs.index(t), concept_IDs.index(s)].astype('float')
							stddev_X2 = numpy.sqrt(big_A[concept_IDs.index(t), concept_IDs.index(t)].astype('float'))
							stddev_Y2 = numpy.sqrt(big_A[concept_IDs.index(s), concept_IDs.index(s)].astype('float'))
							linkStrength2 = cov_XY2 / (stddev_X2 * stddev_Y2)
						else:
							linkStrength1 = 0
							linkStrength2 = 0
						core_links_value.append(math.sqrt(linkStrength1 * linkStrength2))
				
				core_nodes_parents_index = list(ConceptConceptLink.objects.filter(type='type of', source_concept_id__in=core_nodes_index).values_list('id',flat=True))
				
				outer_nodes_index = []
				outer_nodes_name = []
				outer_nodes_terms = []
				outer_links_source = []
				outer_links_target = []
				outer_links_value = []
				
				linkset_sourceIDs = []
				linkset_targetIDs = []
				linkset_values = []
				concept_IDs_subset = list(get_domain_concept_IDs_byConceptType(domain_ID, concept_type_code))
				concept_IDs_manually_excluded = [4239]
				for x in core_nodes_index:
					nz_indices = big_A[concept_IDs.index(x),:].nonzero()[1].tolist()
					nz_indices_filtered = nz_indices
					nz_indices_filtered = list(set(nz_indices_filtered)-set([concept_IDs.index(i) for i in core_nodes_index]))
					nz_indices_filtered = list(set(nz_indices_filtered)-set([concept_IDs.index(i) for i in core_nodes_parents_index]))
					nz_indices_filtered = list(set(nz_indices_filtered).intersection(set(concept_IDs_subset)))					
					concept_IDs_filtered = [concept_IDs[i] for i in nz_indices]
					concept_IDs_filtered = list(set(concept_IDs_filtered)-set(core_nodes_index)) # not core node
					concept_IDs_filtered = list(set(concept_IDs_filtered)-set(core_nodes_parents_index)) # not parent
					concept_IDs_filtered = list(set(concept_IDs_filtered).intersection(set(concept_IDs_subset))) # selected concept type
					concept_IDs_filtered = list(set(concept_IDs_filtered)-set(concept_IDs_manually_excluded)) # manually exclude certain concepts
					nz_indices_filtered = [concept_IDs.index(i) for i in concept_IDs_filtered]					
					if method == 'freq': # big_A are freqs - calculate conditional probability from frequencies
						values = (big_A[concept_IDs.index(x), nz_indices_filtered].astype('float').toarray()[0] / big_A[concept_IDs.index(x), concept_IDs.index(x)].astype('float')).tolist()
					elif method == 'cov': # big_A are covariances - calculate Pearson correlation coefficient from covariance matrix
						cov_XY = big_A[concept_IDs.index(x), nz_indices_filtered].astype('float').toarray()[0]
						stddev_X = numpy.sqrt(big_A[concept_IDs.index(x), concept_IDs.index(x)].astype('float'))
						stddev_Y = numpy.sqrt(big_A[nz_indices_filtered, nz_indices_filtered].astype('float'))
						values = (cov_XY / (stddev_X * stddev_Y)).tolist()[0]
					else:
						values = 0 * len(nz_indices_filtered)						
					linkset_sourceIDs.extend([x for value in values if value > 0])
					linkset_targetIDs.extend([concept_IDs[nz_indices_filtered[i]] for i, value in enumerate(values) if value > 0])
					linkset_values.extend([value for value in values if value > 0])
				linkset_sorted_indices = sorted(range(len(linkset_values)), key=lambda k: linkset_values[k], reverse=True)
				#concepts = Concept.objects.filter(id__in=linkset_targetIDs).prefetch_related('term_set')
				#con_objs = dict([(obj.id, obj) for obj in concepts])
				for ind in linkset_sorted_indices:
					if len(outer_nodes_index) >= node_number:
						break
					else:
						source_ID = linkset_sourceIDs[ind]
						target_ID = linkset_targetIDs[ind]
						value = linkset_values[ind]
						term_set = Concept.objects.get(id=target_ID).term_set.all()
						termsNotContained = True
						for term_i in term_set:
							termsNotContained = termsNotContained and not any(term_i.name in x for x in core_nodes_terms_all)
						if termsNotContained:
							outer_nodes_index.append(target_ID)
							outer_nodes_name.append(Concept.objects.get(id=target_ID).name)
							terms = [];
							for term_i in term_set:
								if len(terms) > 5:
									terms.append('(plus additional terms...)')
									break
								else:
									terms.append(term_i.name)
							outer_nodes_terms.append(terms)
							outer_links_source.append(source_ID)
							outer_links_target.append(target_ID)
							outer_links_value.append(value)
				
				data = json.dumps({
					'core_nodes': {
						'index': core_nodes_index, 
						'name': core_nodes_name,
						'terms': core_nodes_terms}, 
					'core_links': {
						'source': core_links_source, 
						'target': core_links_target, 
						'value': core_links_value}, 
					'outer_nodes': {
						'index': outer_nodes_index, 
						'name': outer_nodes_name,
						'terms': outer_nodes_terms}, 
					'outer_links': {
						'source': outer_links_source, 
						'target': outer_links_target, 
						'value': outer_links_value}
				}, use_decimal=True)
				
			print "time to retrieve network graph data: " + str(time()-start) + " seconds"
				
		except Exception as inst:
			print inst
			traceback.print_exc()
	else:
		data = 'fail'
	#print "number of SQL queries made:", len(connection.queries)
	mimetype = 'application/json'
	return HttpResponse(data, mimetype)

'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Gets user's subresources that contain both source_concept and target_concept
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''		
def get_user_filtSubres(user_ID, source_concept_id, target_concept_id):
	generation = get_user_generation(user_ID)
	cache_key = 'gen-%s-filtSubres_%s_%s_%s' % (str(generation), str(user_ID), str(source_concept_id), str(target_concept_id))
	filtSubres = cache.get(cache_key)
	if not filtSubres:
		filtSubres = Subresource.objects.filter(containing_resource__user__id=user_ID).filter(concepts_contained__id=source_concept_id).filter(concepts_contained__id=target_concept_id)
		cache.set(cache_key, filtSubres, 0)
	return filtSubres
	
'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Fetches user's resources and prepares content for display by UI
called via ajax when a link in network graph is clicked
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''		
def fetch_resources(request):
	max_snippets_per_page = 20 # max items for paginator
	try:
		start = time()
		if request.is_ajax():
			source_concept_id = request.GET.get('source_concept_id', '')
			target_concept_id = request.GET.get('target_concept_id', '')
			user_ID = request.user.id
			
			page = request.GET.get('page')
			generation = get_user_generation(user_ID)
			cache_key = 'gen-%s-fetchres_%s_%s_%s_%s' % (str(generation), str(user_ID), str(source_concept_id), str(target_concept_id), str(page))
			data = cache.get(cache_key)
			if not data:
				subresources = get_user_filtSubres(user_ID, source_concept_id, target_concept_id)
				
				subresource_scores_all = [] # used for ranking subresources
				subresource_json_list = []
				snippet_index_of_subresource = []
				
				source_terms = Term.objects.filter(concept_id=source_concept_id)
				target_terms = Term.objects.filter(concept_id=target_concept_id)
				source_terms_regex = [r"\b"+re.escape(term.name.lower())+r"\b" for term in source_terms]
				source_search_pattern = re.compile("|".join(source_terms_regex))
				target_terms_regex = [r"\b"+re.escape(term.name.lower())+r"\b" for term in target_terms]
				target_search_pattern = re.compile("|".join(target_terms_regex))
				
				for subres_num, subresource in enumerate(subresources):					
					tokenized_sentences = sent_tokenize(subresource.content)
					sentence_scores = []					
					for sentence in tokenized_sentences:
						sentence_score_intersection = 0
						sentence_score_union = 0
						source_terms_in_sentence = len(source_search_pattern.findall(sentence.lower()))
						target_terms_in_sentence = len(target_search_pattern.findall(sentence.lower()))
						sentence_score_intersection = source_terms_in_sentence * target_terms_in_sentence #both terms in sentence
						sentence_score_union = source_terms_in_sentence + target_terms_in_sentence #either term in sentence 
						sentence_scores.append(sentence_score_union)
						if sentence_score_intersection > 0:
							if sentence[-1:] == '.':
								snippet = sentence
							else:
								snippet = sentence + '.'
							
							# store the index of subresource of this snippet
							snippet_index_of_subresource.append(subres_num)
										
							# add highlighting to terms in subresource.content
							subresource_content_mod = subresource.content
							pos_increment = 0
							styletag_start = '<span class="hilite-sentence">'
							styletag_end = '</span>'
							pos_start = subresource_content_mod.lower().index(sentence.lower())
							pos_end = subresource_content_mod.lower().index(sentence.lower())+len(sentence.lower())
							subresource_content_mod = subresource_content_mod[:pos_start+pos_increment] + styletag_start + subresource_content_mod[pos_start+pos_increment:]
							pos_increment = pos_increment + len(styletag_start)
							subresource_content_mod = subresource_content_mod[:pos_end+pos_increment] + styletag_end + subresource_content_mod[pos_end+pos_increment:]
							pos_increment = pos_increment + len(styletag_end)
							pos_increment = 0
							styletag_start = '<span class="hilite-source_concept">'
							styletag_end = '</span>'
							for m in source_search_pattern.finditer(subresource_content_mod.lower()):
								subresource_content_mod = subresource_content_mod[:m.start()+pos_increment] + styletag_start + subresource_content_mod[m.start()+pos_increment:]
								pos_increment = pos_increment + len(styletag_start)
								subresource_content_mod = subresource_content_mod[:m.end()+pos_increment] + styletag_end + subresource_content_mod[m.end()+pos_increment:]
								pos_increment = pos_increment + len(styletag_end)
							pos_increment = 0
							styletag_start = '<span class="hilite-target_concept">'
							styletag_end = '</span>'
							for m in target_search_pattern.finditer(subresource_content_mod.lower()):
								subresource_content_mod = subresource_content_mod[:m.start()+pos_increment] + styletag_start + subresource_content_mod[m.start()+pos_increment:]
								pos_increment = pos_increment + len(styletag_start)
								subresource_content_mod = subresource_content_mod[:m.end()+pos_increment] + styletag_end + subresource_content_mod[m.end()+pos_increment:]
								pos_increment = pos_increment + len(styletag_end)
							
							subresource_json = {
								'resource_id': subresource.containing_resource.id,
								'journal': subresource.containing_resource.journal,
								'name': subresource.name, 
								'type': subresource.type, 
								'content': subresource_content_mod, 
								'snippet': snippet, 
								'url': subresource.url
							}
							subresource_json_list.append(subresource_json)
							
					subresource_scores_all.append(numpy.mean(sentence_scores))
				
				subresource_scores_subset = [subresource_scores_all[i] for i in snippet_index_of_subresource]
				
				# create and append json for subresource ordered by desc subresource_scores
				subresources_json = []
				subresources_sorted_indices = sorted(range(len(subresource_scores_subset)), key=lambda k: subresource_scores_subset[k], reverse=True)
				for ind in subresources_sorted_indices:
					subresources_json.append(subresource_json_list[ind])
				
				subresources_json_paginator = Paginator(subresources_json, max_snippets_per_page)
				subresources_json_page = subresources_json_paginator.page(page)
				subresources_json_page_objects = subresources_json_page.object_list
				
				resources_json = []			
				subset_resource_id_list = [element['resource_id'] for element in subresources_json_page_objects]
				resources = Resource.objects.filter(id__in=subset_resource_id_list).distinct()			
				for resource in resources:
					resources_json.append({
						'id': resource.id,
						'identifier': resource.identifier,
						'type': resource.type, 
						'title': resource.title, 
						'author': resource.author,
						'journal': resource.journal,
						'volume': resource.volume,
						'issue': resource.issue,
						'firstpage': resource.firstpage,
						'lastpage': resource.lastpage,
						'date': resource.date,
						'publisher': resource.publisher,
						'url': resource.url
					})
					
				data = json.dumps({
					'resources': resources_json, 
					'subresources': subresources_json_page_objects,
					'current_page': subresources_json_page.number, 
					'num_pages': subresources_json_paginator.num_pages, 
					'has_previous': subresources_json_page.has_previous(), 
					'has_next': subresources_json_page.has_next()
				}, use_decimal=True)
				
				cache.set(cache_key, data, 0)
		else:
			data = 'fail'
		
		print "time to fetch resources: " + str(time()-start) + " seconds"
	except Exception as inst:
		print inst
		traceback.print_exc()
	mimetype = 'application/json'
	#print "number of SQL queries made:", len(connection.queries)
	return HttpResponse(data, mimetype)
