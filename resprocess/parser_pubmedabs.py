# Parser 
# PubMed Abstracts
import re
from bs4 import BeautifulSoup
import urllib2, xml.dom.minidom

'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Gets metadata information

Returns metadata, which is a list of the following:
0 identifier
1 type
2 language
3 title
4 date
5 publisher
6 author
7 journal
8 volume
9 issue
10 firstpage
11 lastpage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
def get_metadata(url, soup):
			
	meta_tags = soup.find_all('meta')
	metadata = ['']*12
	
	for meta_tag in meta_tags:
		try:
			if 'ncbi_uidlist' in meta_tag['name']:
				metadata[0] = "pubmed/" + meta_tag['content']
				break
		except: pass
		
	metadata[1] = 'abstract'
	
	metadata[2] = 'en'
	
	#connect to the appropriate abstract through Entrez
	conn = urllib2.Request("http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id=" + metadata[0])
	response = xml.dom.minidom.parse(urllib2.urlopen(conn))
	
	try:
		metadata[3] = response.getElementsByTagName("ArticleTitle")[0].childNodes[0].data
	except: pass
		
	try:
		y = response.getElementsByTagName("ArticleDate")[0].getElementsByTagName("Year")[0].childNodes[0].data
		m = response.getElementsByTagName("ArticleDate")[0].getElementsByTagName("Month")[0].childNodes[0].data
		d = response.getElementsByTagName("ArticleDate")[0].getElementsByTagName("Day")[0].childNodes[0].data
		metadata[4] = str(y) + "-" + str(m) + "-" + str(d)
	except: pass
	
	try:
		metadata[5] = response.getElementsByTagName("Journal")[0].getElementsByTagName("Title")[0].childNodes[0].data
	except: pass
		
	authors = ''
	authorlist = response.getElementsByTagName("AuthorList")[0].getElementsByTagName("Author")
	for author in authorlist:
		try:
			name = author.getElementsByTagName("ForeName")[0].childNodes[0].data + " " + author.getElementsByTagName("LastName")[0].childNodes[0].data
			authors += name + ";"
		except: pass
	metadata[6] = authors
	
	try:
		metadata[7] = response.getElementsByTagName("Journal")[0].getElementsByTagName("ISOAbbreviation")[0].childNodes[0].data
	except: pass
	
	try:
		metadata[8] = response.getElementsByTagName("JournalIssue")[0].getElementsByTagName("Volume")[0].childNodes[0].data
	except: pass
	
	try:
		metadata[9] = response.getElementsByTagName("JournalIssue")[0].getElementsByTagName("Issue")[0].childNodes[0].data
	except: pass
	
	metadata[10] = None
	metadata[11] = None	
	
	return metadata

'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Returns figures as a list of tuples
Tuple contains:
- figure name
- figure caption
- figure small pic URL
- figure medium pic URL (may return 404)
- figure large pic URL (may return 404)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''			
def get_figures(url, soup):
	# there are generally no figures in abstracts
	return []

'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Returns content paragraphs
(Discards figure and tables with captions; these are produced by
	separate functions)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''	
def get_paragraphs(url, soup):

	meta_tags = soup.find_all('meta')
	
	for meta_tag in meta_tags:
		try:
			if 'ncbi_uidlist' in meta_tag['name']:
				PMID = str(meta_tag['content'])
				break
		except: pass
			
	conn = urllib2.Request("http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id=" + PMID)
	response = xml.dom.minidom.parse(urllib2.urlopen(conn))
	
	paragraph_list = []
	paragraph_list.append(response.getElementsByTagName("Abstract")[0].getElementsByTagName("AbstractText")[0].childNodes[0].data)
	return paragraph_list