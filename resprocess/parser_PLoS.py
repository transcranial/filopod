# Parser 
# PLoS
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
			if 'citation_doi' in meta_tag['name'].lower():
				metadata[0] = meta_tag['content'].encode('utf-8','ignore')
				break
		except: pass
		
	metadata[1] = 'journal article'
	
	metadata[2] = 'en'
	
	for meta_tag in meta_tags:	
		try:
			if 'citation_title' in meta_tag['name'].lower():
				metadata[3] = meta_tag['content'].encode('utf-8','ignore')
				break
		except: pass
	
	for meta_tag in meta_tags:	
		try:
			if 'citation_date' in meta_tag['name'].lower():
				metadata[4] = meta_tag['content'].encode('utf-8','ignore')
				break
		except: pass
	
	for meta_tag in meta_tags:	
		try:
			if 'citation_publisher' in meta_tag['name'].lower():
				metadata[5] = meta_tag['content'].encode('utf-8','ignore')
				break
		except: pass
		
	authors = ''
	for meta_tag in meta_tags:
		try:
			if meta_tag['name'].lower() == 'citation_author':
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
	figure_list = []
	
	url_base = url[:url.find('.org')] + '.org'
	
	figures = soup.find_all(class_='figure')
	for figure in figures:
		try:
			name = figure.find('strong').text.encode('utf-8','ignore').strip()
		except:
			name = ''
			pass
		figure.find(class_='figure-inline-download').decompose()
		caption = ''
		caps = figure.find_all('p')
		for cap in caps:
			caption = caption + ' ' + cap.text.encode('utf-8','ignore')
		caption = re.compile('([\t\n]+)|(\s\s)+').sub(' ', caption)
		caption = re.compile('(\s\s)+').sub(' ', caption)
		smallpic_url = url_base + figure.find(class_='img').find('img')['src']
		mediumpic_url = ''
		largepic_url = url_base + figure.find(class_='img').find('a')['href']
		figure_list_item = name, caption, smallpic_url, mediumpic_url, largepic_url
		figure_list.append(figure_list_item)
	return figure_list

'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Returns content paragraphs
(Discards figure and tables with captions; these are produced by
	separate functions)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''	
def get_paragraphs(url, soup):
	paragraph_list = []
	figures = soup.find_all(class_='figure')
	for figure in figures:
		figure.decompose()
	sections = soup.find_all(class_='section')
	for section in sections:
		paragraphs = section.find_all('p')
		for paragraph in paragraphs:
			paragraph = paragraph.text.encode('utf-8','ignore')
			paragraph = re.compile('([\t\n]+)|(\s\s)+').sub(' ', paragraph)
			paragraph = re.compile('(\s\s)+').sub(' ', paragraph)
			paragraph_list.append(paragraph)
	return paragraph_list