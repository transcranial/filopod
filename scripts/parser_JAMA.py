# Parser 
# JAMA
from bs4 import BeautifulSoup
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
def get_metadata(url, entry_html_source):
    soup = BeautifulSoup(entry_html_source.decode('utf-8'), 'html5lib')
    
    meta_tags = soup.find_all('meta')
    metadata = ['']*12
    
    for meta_tag in meta_tags:
        try:
            if 'citation_doi' in meta_tag['name'].lower():
                metadata[0] = meta_tag['content']
                break
        except: pass
    
    metadata[1] = 'journal article'
    
    metadata[2] = 'en'
    
    for meta_tag in meta_tags:
        try:
            if 'citation_title' in meta_tag['name'].lower():
                metadata[3] = meta_tag['content']
                break
        except: pass
    
    for meta_tag in meta_tags:    
        try:
            if 'citation_date' in meta_tag['name'].lower():
                metadata[4] = meta_tag['content']
                break
        except: pass
        
    for meta_tag in meta_tags:
        try:
            if 'citation_publisher' in meta_tag['name'].lower():
                metadata[5] = meta_tag['content']
                break
        except: pass
    
    authors = ''
    for meta_tag in meta_tags:
        try:
            if meta_tag['name'].lower() == 'citation_authors':
                authors = meta_tag['content']
                break
            elif meta_tag['name'].lower() == 'citation_author':
                authors += meta_tag['content'] + '; '
        except: pass
    metadata[6] = authors
    
    for meta_tag in meta_tags:    
        try:
            if 'citation_journal_title' in meta_tag['name'].lower():
                metadata[7] = meta_tag['content']
                break
        except: pass
    
    for meta_tag in meta_tags:    
        try:
            if 'citation_volume' in meta_tag['name'].lower():
                metadata[8] = meta_tag['content']
                break
        except: pass
    
    for meta_tag in meta_tags:    
        try:
            if 'citation_issue' in meta_tag['name'].lower():
                metadata[9] = meta_tag['content']
                break
        except: pass
    
    for meta_tag in meta_tags:    
        try:
            if 'citation_firstpage' in meta_tag['name'].lower():
                metadata[10] = meta_tag['content']
                break
        except: pass
    
    for meta_tag in meta_tags:    
        try:
            if 'citation_lastpage' in meta_tag['name'].lower():
                metadata[11] = meta_tag['content']
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
def get_figures(url, entry_html_source):
    soup = BeautifulSoup(entry_html_source.decode('utf-8'), 'html5lib')
    figure_list = []
    
    url_base = url[:url.find('jamanetwork.com')] + 'jamanetwork.com'
    
    figures = soup.find_all(class_=re.compile('^Figure\s*'))
    for figure in figures:
        try:
            name = figure.find(class_=re.compile('figureLabel*')).text
        except:
            name = ''
            pass
        try:
            caption = figure.find(class_='figureCaption').text
        except:
            caption = ''
            pass
        caption = re.compile('([\t\n]+)|(\s\s)+').sub(' ', caption)
        caption = re.compile('(\s\s)+').sub(' ', caption)
        smallpic_url = url_base + figure.find(class_=re.compile('inlineFigureImageContainer')).find('img')['src']
        mediumpic_url = ''
        largepic_url = url_base + figure.find(class_=re.compile('figureDialog')).find('img')['src']
        figure_list_item = name, caption, smallpic_url, mediumpic_url, largepic_url
        figure_list.append(figure_list_item)
    tables = soup.find_all(class_=re.compile('^Table\s*'))
    for table in tables:
        try:
            name = table.find('strong').text.strip()
            table.find('strong').decompose()
        except:
            name = ''
            pass
        try:
            links = table.find_all('a')
            for link in links:
                link.decompose()
        except: pass
        caption = table.text.replace('| ','').strip()
        caption = re.compile('([\t\n]+)|(\s\s)+').sub(' ', caption)
        caption = re.compile('(\s\s)+').sub(' ', caption)
        smallpic_url = url_base + table.find(class_=re.compile('inlineFigureImageContainer')).find('img')['src']
        mediumpic_url = ''
        largepic_url = url_base + table.find(class_=re.compile('tableDialog')).find('img')['src']
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
    soup_section = soup.find(id='tab1')
    paragraph_list = []
    refs = soup_section.find_all(class_='reflink')
    for ref in refs:
        ref.decompose()
    paragraphs = soup_section.find_all(class_=re.compile('^Paragraph\s*'))
    for paragraph in paragraphs:
        paragraph = paragraph.text
        paragraph = re.compile('([\t\n]+)|(\s\s)+').sub(' ', paragraph)
        paragraph = re.compile('(\s\s)+').sub(' ', paragraph)
        paragraph_list.append(paragraph)
    return paragraph_list