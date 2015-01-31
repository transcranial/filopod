from main.models import *
#from nltk.tokenize import sent_tokenize
from scipy.sparse import coo_matrix, csr_matrix, vstack
from scipy import int16
from numpy import array
import math
from time import time
import traceback
import sys
import cPickle as pickle
import zlib
import xml.etree.cElementTree as ET
import re2 as re

'''pickle and compress obj'''
def pickle_zdumps(obj):
	return zlib.compress(pickle.dumps(obj,pickle.HIGHEST_PROTOCOL),9)

'''unpickle and decompress obj'''
def pickle_zloads(zstr):
	return pickle.loads(zlib.decompress(zstr))
	
'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
crunch Pubmed Abstracts
Filopod admin account: ID=9
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''		
def run():
	sys.stdout.write("~~~~loading concepts and term lists... ")
	start = time()
	file = open('scripts\MESH_concept_and_terms_tuple.pkl','rb')
	(tot_concepts, concept_IDs, term_lists) = pickle.loads(file.read())
	file.close()
	print "%.2f" % (time()-start), "seconds"
	
	for filenumber in [str(766-x) for x in range(20)]:
		print "FILENUM: " + filenumber
		row = []
		col = []
		data = []
		
		sys.stdout.write("~~~~parsing XML file... ")
		start = time()
		tree = ET.parse("..\..\PubMed\zip\medline13n0%s.xml" % filenumber)
		root = tree.getroot()
		citations = root.findall("MedlineCitation")
		sys.stdout.write("# citations: %d... " % len(citations))
		abstracts = []
		res_list = []
		for citation in citations:
			abstract_ET = citation.find("Article/Abstract")
			if abstract_ET is not None:
				abstract_textlist = []
				for t in abstract_ET.findall("AbstractText"):
					if t is not None:
						if t.text is not None:
							abstract_textlist.append(t.text)
				abstract = ' '.join(abstract_textlist)
				abstracts.append(abstract)
				res_tag = citation.find("PMID")
				if res_tag is None:
					url = ''
					identifier = ''
				else:
					identifier = res_tag.text
					url = "http://www.ncbi.nlm.nih.gov/pubmed/" + identifier
				res_tag = citation.find("Article/Language")
				if res_tag is None:
					language = ''
				else:
					language = res_tag.text[:2]
				res_tag = citation.find("Article/ArticleTitle")
				if res_tag is None:
					title = ''
				else:
					title = res_tag.text[:300]
				res_tag = citation.find("Article/Journal/JournalIssue/PubDate/Year")
				if res_tag is None:
					date = ''
				else:
					date = res_tag.text
				author_ET = citation.find("Article/AuthorList")
				if author_ET is not None:
					author_list = []
					for t in author_ET.getchildren():
						tt = t.find("LastName")
						if tt is not None:
							ttt = tt.find("Initials")
							if ttt is not None:
								author_list.append(tt.text+" "+ttt.text)
							else:
								author_list.append(tt.text)
					author = ', '.join(author_list)
					author = author[:767]	
				res_tag = citation.find("Article/Journal/ISOAbbreviation")
				if res_tag is None:
					journal = ''
				else:
					journal = res_tag.text[:50]
				res_tag = citation.find("Article/Journal/JournalIssue/Volume")
				if res_tag is None:
					volume = ''
				else:
					volume = res_tag.text
				res_tag = citation.find("Article/Journal/JournalIssue/Issue")
				if res_tag is None:
					issue = ''
				else:
					issue = res_tag.text
				res_tag = citation.find("Article/Pagination/MedlinePgn")
				if res_tag is None:
					firstpage = ''
				else:
					firstpage = res_tag.text.split('-')[0]
				res = Resource(identifier = identifier,
					type = "pubmed_abstract",
					language = language,
					title = title,
					date = date,
					publisher = '',
					author = author,
					journal = journal,
					volume = volume,
					issue = issue,
					firstpage = firstpage,
					lastpage = '',
					url = url,
					html_source = '')
				res_list.append(res)
		sys.stdout.write("# abstracts: %d... " % len(abstracts))
		print "%.2f" % (time()-start), "seconds"
		
		sys.stdout.write("~~~~crunching abstracts... ")
		start = time()
		abstract_conceptIDs_contained = [[] for i in range(len(abstracts))]
		for i, con_ID in enumerate(concept_IDs):
			if i % 1000 == 0:
				sys.stdout.write(str(int(i*100/tot_concepts)))
				sys.stdout.write("% ")
			term_list = term_lists[i]
			terms_regex = [r"\b"+re.escape(term.lower())+r"\b" for term in term_list]
			search_pattern = re.compile("|".join(terms_regex))	
		
			for abstract_num, abstract in enumerate(abstracts):
				wordcount = len(search_pattern.findall(abstract.lower()))
				if wordcount > 0:
					row.append(abstract_num)
					col.append(i)
					data.append(wordcount)
					abstract_conceptIDs_contained[abstract_num].append(con_ID)
		sys.stdout.write("... ")
		print "%.2f" % (time()-start), "seconds"	
		
		sys.stdout.write("~~~~saving file containing tuple of database object models... ")
		start = time()
		res_abstract_containedcon_tuplelist = []
		for abstract_num in range(len(abstracts)):
			res_abstract_containedcon_tuplelist.append((res_list[abstract_num], abstracts[abstract_num], abstract_conceptIDs_contained[abstract_num]))
		path = "scripts\\files_for_ec2\\res_abstract_containedcon_tuplelist_medline13n0%s.pkl" % filenumber
		file = open(path,'wb')
		file.write(pickle_zdumps(res_abstract_containedcon_tuplelist))
		file.close()
		print "%.2f" % (time()-start), "seconds"
		
		sys.stdout.write("~~~~creating target_A matrix... ")
		start = time()
		target_A = coo_matrix((array(data),(array(row),array(col))),shape=(len(abstracts),tot_concepts),dtype=int16)
		#now convert target_A into a scipy csr_matrix (sparse matrix)
		target_A = target_A.tocsr()
		path = "scripts\\pubmed_matrices\\rawA_medline13n0%s.pkl" % filenumber
		file = open(path,'wb')
		file.write(pickle_zdumps(target_A))
		file.close()
		print "%.2f" % (time()-start), "seconds"
	
	
	
	
	
	
	
	# Following is to be run on EC2 to reduce network latency #
	'''
	for (res, abstract, concept_IDs_contained) in res_abstract_containedcon_tuplelist:
		res.save()
		res.user.add(9)
		res.domain.add(1)
		subres = Subresource.objects.create(containing_resource = res,
			name = 'paragraph ' + str(i),
			type = 'abstract',
			content = abstract)
		subres.concepts_contained.add(*concept_IDs_contained)
	'''
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
