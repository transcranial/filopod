# Parser 
# Nature
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
			if 'dc.identifier' in meta_tag['name'].lower():
				metadata[0] = meta_tag['content'].encode('utf-8','ignore')
				break
			elif 'citation_doi' in meta_tag['name'].lower():
				metadata[0] = meta_tag['content'].encode('utf-8','ignore')
				break
		except: pass
		
	metadata[1] = 'journal article'
	
	for meta_tag in meta_tags:	
		try:
			if 'dc.language' in meta_tag['name'].lower():
				metadata[2] = meta_tag['content'].encode('utf-8','ignore')
				break
		except: pass
	
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
			if 'dc.date' in meta_tag['name'].lower():
				metadata[4] = meta_tag['content'].encode('utf-8','ignore')
				break
			elif 'citation_date' in meta_tag['name'].lower():
				metadata[4] = meta_tag['content'].encode('utf-8','ignore')
				break
		except: pass
	
	for meta_tag in meta_tags:	
		try:
			if 'dc.rights' in meta_tag['name'].lower():
				metadata[5] = meta_tag['content'].encode('utf-8','ignore')
				break
		except: pass
		
	authors = ''
	for meta_tag in meta_tags:
		try:
			if meta_tag['name'].lower() == 'citation_authors':
				authors = meta_tag['content'].encode('utf-8','ignore')
				break
			elif meta_tag['name'].lower() == 'citation_author':
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
			elif 'prism.startingpage' in meta_tag['name'].lower():
				metadata[10] = meta_tag['content'].encode('utf-8','ignore')
				break
		except: pass
	
	for meta_tag in meta_tags:	
		try:
			if 'citation_lastpage' in meta_tag['name'].lower():
				metadata[11] = meta_tag['content'].encode('utf-8','ignore')
				break
			elif 'prism.endingpage' in meta_tag['name'].lower():
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
	figure_list = []
	
	url_base = 'http://www.nature.com'
	
	figures = soup.find_all(id=re.compile('(^f\d)|(^fig\d)'))
	for figure in figures:		
		name = figure['id']
		legend = figure.find(class_='legend')
		if legend:
			legend = legend.text.encode('utf-8','ignore')
		description = figure.find(class_='description')
		if description:
			description = description.text.encode('utf-8','ignore')
		caption = legend + ' ' + description
		caption = re.compile('([\t\n]+)|(\s\s)+').sub(' ', caption)
		caption = re.compile('(\s\s)+').sub(' ', caption)
		#e.g. images_article/nature#####-f1.2.jpg
		mediumpic_url = url_base + figure.img['src']
		#e.g. carousel/nature#####-f1.2.jpg
		smallpic_url = url_base + figure.img['src'].replace('images_article','carousel') 
		#e.g. images/nature#####-f1.2.jpg
		largepic_url = url_base + figure.img['src'].replace('images_article','images')
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
	figures = soup.find_all(class_='figure-table')
	for fig in figures:
		fig.decompose()
	figures = soup.find_all(class_='figure')
	for fig in figures:
		fig.decompose()
	figures = soup.find_all(class_='table')
	for fig in figures:
		fig.decompose()
	paragraphs = soup.find_all('p')
	for paragraph in paragraphs:
		if not paragraph.has_attr('class'):
			paragraph = paragraph.text.encode('utf-8','ignore')
			paragraph = re.compile('([\t\n]+)|(\s\s)+').sub(' ', paragraph)
			paragraph = re.compile('(\s\s)+').sub(' ', paragraph)
			if paragraph:
				paragraph_list.append(paragraph)
	return paragraph_list