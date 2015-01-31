# Parser 
# RadioGraphics
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
def get_metadata(url, entry_html_source):
    soup = BeautifulSoup(entry_html_source.decode('utf-8'), 'html5lib')
            
    meta_tags = soup.find_all('meta')
    metadata = ['']*12
    
    metadata[0] = ''
    
    metadata[1] = 'journal article'
    
    metadata[2] = 'en'
    
    for meta_tag in meta_tags:    
        try:
            if 'dc.title' in meta_tag['name'].lower():
                metadata[3] = meta_tag['content']
                break
        except: pass
    
    for meta_tag in meta_tags:    
        try:
            if 'dc.date' in meta_tag['name'].lower():
                metadata[4] = meta_tag['content']
                break
        except: pass
    
    for meta_tag in meta_tags:    
        try:
            if 'dc.publisher' in meta_tag['name'].lower():
                metadata[5] = meta_tag['content']
                break
        except: pass
        
    authors = ''
    for meta_tag in meta_tags:
        try:
            if meta_tag['name'].lower() == 'dc.creator':
                authors += meta_tag['content'] + '; '
        except: pass
    metadata[6] = authors
    
    metadata[7] = 'RadioGraphics'
    
    metadata[8] = ''
    metadata[9] = ''
    metadata[10] = ''
    metadata[11] = ''
    
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
def get_figures(url, entry_html_source):
    soup = BeautifulSoup(entry_html_source.decode('utf-8'), 'html5lib')
    figure_list = []    
    url_base = 'http://pubs.rsna.org'
    figures = soup.find_all(id=re.compile('(^F\d)|(^fig\d\d$)'))
    for figure in figures:
        name = figure['id']    
        try:
            caption = figure.text
        except: pass
        for fig in figure.find_all('img'):
            smallpic_url = ''
            mediumpic_url = url_base + fig['src']
            largepic_url = mediumpic_url.replace('gif','jpeg') 
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
def get_paragraphs(url, entry_html_source):
    soup = BeautifulSoup(entry_html_source.decode('utf-8'), 'html5lib')
    paragraph_list = []
    refs = soup.find_all(class_='ref')
    for ref in refs:
        try:
            ref.decompose()
        except: pass
    figrefs = soup.find_all(id=re.compile('^ref'))
    for fref in figrefs:
        try:
            fref.decompose()
        except: pass
    figs = soup.find_all(id=re.compile('(^F\d)|(^fig\d\d$)'))
    for fig in figs:
        try:
            fig.decompose()
        except: pass
    paragraphs = soup.find_all('p')
    for paragraph in paragraphs:
        try:
            paragraph = paragraph.text
            paragraph = re.compile(u'(\(\))|(\(,\))|(\(,,\))|(\(,,,\))|(\(\u2013\))|( \(\))|( \(,\))|( \(,,\))|( \(,,,\))|( \(\u2013\))').sub('', paragraph)
            if not (paragraph == u''):
                paragraph_list.append(paragraph)
        except: pass
    return paragraph_list