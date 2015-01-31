# Parser 
# Common Journal Format
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
			if 'dc.publisher' in meta_tag['name'].lower():
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
	figure_list = []
	
	url_base = url
	for meta_tag in soup.find_all('meta'):	
		try:
			if 'citation_public_url' in meta_tag['name'].lower():
				url_base = meta_tag['content']
				break
		except: pass
	url_base = url_base[:url_base.rfind('/')+1]
	
	figures = soup.find_all(id=re.compile('^F\d'))
	for figure in figures:
		name = figure['id']
		caption = figure.find(class_='fig-caption').text.encode('utf-8','ignore')
		caption = re.compile('([\t\n]+)|(\s\s)+').sub(' ', caption)
		caption = re.compile('(\s\s)+').sub(' ', caption)
		#e.g. F1.small.gif
		smallpic_url = url_base + figure.find('img')['src']
		#e.g. F1.medium.gif
		mediumpic_url = url_base + figure.find('img')['src'].replace('small','medium') 
		#e.g. F1.large.jpg
		largepic_url = url_base + figure.find('img')['src'].replace('small','large').replace('gif','jpg') 
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
	figures = soup.find_all(id=re.compile('^F\d'))
	tables = soup.find_all(id=re.compile('^T\d'))
	acknowledgements = soup.find_all(class_='section ack')
	footnotes = soup.find_all(class_='section fn-group')
	bio = soup.find_all(class_='bio')
	refs = soup.find_all(class_=re.compile('(xref-bibr)|(xref-sep)'))
	for fig in figures:
		fig.decompose()
	for table in tables:
		table.decompose()
	for sec in acknowledgements:
		sec.decompose()
	for sec in footnotes:
		sec.decompose()
	for sec in bio:
		sec.decompose()
	for ref in refs:
		if ref.parent.name == 'sup':
			ref.decompose()
	paragraphs = soup.find_all(id=re.compile('^p-\d'))
	for paragraph in paragraphs:
		paragraph = paragraph.text.encode('utf-8','ignore')
		paragraph = re.compile('([\t\n]+)|(\s\s)+').sub(' ', paragraph)
		paragraph = re.compile('(\s\s)+').sub(' ', paragraph)
		paragraph = re.compile('(\s\s)+').sub(' ', paragraph)
		paragraph_list.append(paragraph)
	return paragraph_list