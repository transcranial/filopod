# Parser 
# NEJM
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
			if 'doi' in meta_tag['name'].lower():
				metadata[0] = meta_tag['content'].encode('utf-8','ignore')
				break
		except: pass
		
	metadata[1] = 'journal article'
	
	metadata[2] = 'en'
	
	metadata[3] = soup.title.string.encode('utf-8','ignore')
	
	for meta_tag in meta_tags:	
		try:
			if 'evt-dt' in meta_tag['name'].lower():
				metadata[4] = meta_tag['content'].encode('utf-8','ignore')
				break
		except: pass
	
	metadata[5] = 'New England Journal of Medicine'
		
	metadata[6] = ''
	
	metadata[7] = 'New England Journal of Medicine'
	
	metadata[8] = None
	metadata[9] = None
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
- figure medium pic URL
- figure large pic URL 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''			
def get_figures(url, soup):
	#In NEJM, Figures are repeated twice, once within 'abstract' tab and once within the 'article' tab
	abstract_tab = soup.find(id='abstract')
	if abstract_tab:
		abstract_tab.decompose()

	figure_list = []
	
	url_base = 'http://www.nejm.org'
	
	figures = soup.find_all(class_='fig')
	# tables in NEJM are figures
	figures.extend(soup.find_all(class_='table'))
	for figure in figures:		
		name = figure.find(class_='figureTitle').text
		caption = figure.find(class_='figureCaption').text.encode('utf-8','ignore')
		caption = re.compile('([\t\n]+)|(\s\s)+').sub(' ', caption)
		caption = re.compile('(\s\s)+').sub(' ', caption)
		#e.g. images/small/nejm#########_f1.gif
		smallpic_url = url_base + figure.img['src']
		#e.g. images/medium/nejm#########_f1.gif
		mediumpic_url = url_base + figure.img['src'].replace('small','medium') 
		#e.g. images/large/nejm#########_f1.jpeg
		largepic_url = url_base + figure.img['src'].replace('small','large').replace('gif','jpeg') 
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
	ft = soup.find_all(class_='figureTitle')
	fl = soup.find_all(class_='figureLink')
	fc = soup.find_all(class_='figureCaption')
	refs = soup.find_all(class_='ref')
	for f in ft:
		f.decompose()
	for f in fl:
		f.decompose()
	for f in fc:
		f.decompose()
	for ref in refs:
		ref.decompose()
	paragraphs = soup.find_all('p')
	for paragraph in paragraphs:
		if not paragraph.has_attr('class'):
			paragraph = paragraph.text.encode('utf-8','ignore')
			paragraph = re.compile('([\t\n]+)|(\s\s)+').sub(' ', paragraph)
			paragraph = re.compile('(\s\s)+').sub(' ', paragraph)
			if paragraph:
				paragraph_list.append(paragraph)
	return paragraph_list