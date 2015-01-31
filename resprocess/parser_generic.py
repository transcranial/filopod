# Parser 
# Generic
import re

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
			if 'identifier' in meta_tag['name'].lower():
				metadata[0] = meta_tag['content'].encode('utf-8','ignore')
				break
		except: pass
	
	metadata[3] = soup.title.string.encode('utf-8','ignore')
	
	for meta_tag in meta_tags:	
		try:
			if 'date' in meta_tag['name'].lower():
				metadata[4] = meta_tag['content'].encode('utf-8','ignore')
				break
		except: pass
	
	for meta_tag in meta_tags:	
		try:
			if 'author' in meta_tag['name'].lower():
				metadata[6] = meta_tag['content'].encode('utf-8','ignore')
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
	return []

'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Returns content paragraphs
(Discards figure and tables with captions; these are produced by
	separate functions)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''	
def get_paragraphs(url, soup):
	paragraph_list = []
	paragraphs = soup.find_all('p')
	for paragraph in paragraphs:
		paragraph = paragraph.text.encode('utf-8','ignore')
		paragraph = re.compile('([\t\n]+)|(\s\s)+').sub(' ', paragraph)
		paragraph = re.compile('(\s\s)+').sub(' ', paragraph)
		paragraph = re.compile('(\s\s)+').sub(' ', paragraph)
		paragraph_list.append(paragraph)
	return paragraph_list