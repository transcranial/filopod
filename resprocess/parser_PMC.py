# Parser 
# PubMed Central
import re
from bs4 import BeautifulSoup

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
			if 'citation_abstract_html_url' in meta_tag['name'].lower():
				identifier = meta_tag['content']
				identifier = t[t.find('PMC'):t.rfind('/')]
				metadata[0] = identifier.encode('utf-8','ignore')
				break
		except: pass
		
	metadata[1] = 'journal article'
	
	metadata[2] = 'en'
	
	for meta_tag in meta_tags:	
		try:
			if 'dc.title' in meta_tag['name'].lower():
				metadata[3] = meta_tag['content'].encode('utf-8','ignore')
				break
			elif 'citation_title' in meta_tag['name'].lower():
				metadata[3] = meta_tag['content'].encode('utf-8','ignore')
				break
		except: pass
	
	for meta_tag in meta_tags:	
		try:
			if 'citation_date' in meta_tag['name'].lower():
				metadata[4] = meta_tag['content'].encode('utf-8','ignore')
				break
			elif 'dc.date' in meta_tag['name'].lower():
				metadata[4] = meta_tag['content'].encode('utf-8','ignore')
				break
		except: pass
	
	for meta_tag in meta_tags:	
		try:
			if 'dc.publisher' in meta_tag['name'].lower():
				metadata[5] = meta_tag['content'].encode('utf-8','ignore')
				break
		except: pass
		
	authors = ''
	for meta_tag in meta_tags:
		try:
			if 'citation_authors' in meta_tag['name'].lower():
				authors = meta_tag['content'].encode('utf-8','ignore')
				break
			elif 'dc.contributor' in meta_tag['name'].lower():
				authors += meta_tag['content'].encode('utf-8','ignore') + '; '
		except: pass
	metadata[6] = authors
	
	for meta_tag in meta_tags:	
		try:
			if 'citation_journal_title' in meta_tag['name'].lower():
				metadata[7] = meta_tag['content'].encode('utf-8','ignore')
				break
		except: pass
	
	for meta_tag in meta_tags:	
		try:
			if 'citation_volume' in meta_tag['name'].lower():
				metadata[8] = meta_tag['content'].encode('utf-8','ignore')
				break
		except: pass
	
	for meta_tag in meta_tags:	
		try:
			if 'citation_issue' in meta_tag['name'].lower():
				metadata[9] = meta_tag['content'].encode('utf-8','ignore')
				break
		except: pass
	
	for meta_tag in meta_tags:	
		try:
			if 'citation_firstpage' in meta_tag['name'].lower():
				metadata[10] = meta_tag['content'].encode('utf-8','ignore')
				break
		except: pass
	
	for meta_tag in meta_tags:	
		try:
			if 'citation_lastpage' in meta_tag['name'].lower():
				metadata[11] = meta_tag['content'].encode('utf-8','ignore')
				break
		except: pass
	
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
	# figure links at PMC trigger downloads, cannot display
	return []

'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Returns content paragraphs
(Discards figure and tables with captions; these are produced by
	separate functions)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''	
def get_paragraphs(url, soup):
	html_source = str(soup)
	html_source = html_source[html_source.find('<html'):]
	soup = BeautifulSoup(html_source, 'html5lib')
	paragraph_list = []
	paragraphs = soup.find_all(id=re.compile('^P\d'))
	for paragraph in paragraphs:
		paragraph = paragraph.text.encode('utf-8','ignore')
		paragraph = re.compile('([\t\n]+)|(\s\s)+').sub(' ', paragraph)
		paragraph = re.compile('(\s\s)+').sub(' ', paragraph)
		paragraph_list.append(paragraph)
	return paragraph_list