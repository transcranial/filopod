# Parser 
# Brain
# based on HighWire Common Journal Format
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
    
    for meta_tag in meta_tags:
        try:
            if 'dc.identifier' in meta_tag['name'].lower():
                metadata[0] = meta_tag['content']
                break
            elif 'citation_doi' in meta_tag['name'].lower():
                metadata[0] = meta_tag['content']
                break
        except: pass
        
    metadata[1] = 'journal article'
    
    for meta_tag in meta_tags:
        try:
            if 'dc.language' in meta_tag['name'].lower():
                metadata[2] = meta_tag['content']
                break
        except: pass
    
    for meta_tag in meta_tags:
        try:
            if 'dc.title' in meta_tag['name'].lower():
                metadata[3] = meta_tag['content']
                break
            elif 'citation_title' in meta_tag['name'].lower():
                metadata[3] = meta_tag['content']
                break
        except: pass
    
    for meta_tag in meta_tags:
        try:
            if 'dc.date' in meta_tag['name'].lower():
                metadata[4] = meta_tag['content']
                break
            elif 'citation_date' in meta_tag['name'].lower():
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
    url_base = url[:url.rfind('/')+1]
    figures = soup.find_all(id=re.compile('^F\d'))
    for figure in figures:
        name = figure['id']
        try:
            name = figure.find(class_='fig-label').text
        except: pass
        caption = figure.find(class_='fig-caption').text
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
def get_paragraphs(url, entry_html_source):
    soup = BeautifulSoup(entry_html_source.decode('utf-8'), 'html5lib')
    paragraph_list = []
    figures = soup.find_all(id=re.compile('^F\d'))
    tables = soup.find_all(id=re.compile('^T\d'))
    acknowledgements = soup.find_all(class_='section ack')
    footnotes = soup.find_all(class_='section fn-group')
    license = soup.find_all(class_='license')
    bio = soup.find_all(class_='bio')
    notes = soup.find_all(class_='section notes')
    contrib = soup.find_all(class_='contributors')
    refs = soup.find_all(class_=re.compile('(xref-bibr)|(xref-sep)'))
    super = soup.find_all('sup')
    for fig in figures:
        try:
            fig.decompose()
        except: pass
    for table in tables:
        try:
            table.decompose()
        except: pass
    for sec in acknowledgements:
        try:
            sec.decompose()
        except: pass
    for sec in footnotes:
        try:
            sec.decompose()
        except: pass
    for sec in license:
        try:
            sec.decompose()
        except: pass
    for sec in bio:
        try:
            sec.decompose()
        except: pass
    for sec in notes:
        try:
            sec.decompose()
        except: pass
    for contr in contrib:
        try:
            contr.decompose()
        except: pass
    #for ref in refs:
    #    try:
    #        ref.decompose()
    #    except: pass
    for sup in super:
        try:
            sup.decompose()
        except: pass
    try:
        abstract_paragraphs = []
        abstract = soup.find(class_='section abstract')
        ap = abstract.find_all(id=re.compile('^p-\d'))
        for paragraph in ap:
            abstract_paragraphs.append(paragraph.text)
        paragraph_list.append(' '.join(abstract_paragraphs))
        abstract.decompose()
    except: pass
    paragraphs = soup.find_all(id=re.compile('^p-\d'))
    for paragraph in paragraphs:
        try:
            paragraph = paragraph.text
            #paragraph = re.compile('\s\([\w .]*[;, ]+[\w .]*[;, ]+[\w .]*\)').sub('', paragraph)
            #paragraph = re.compile('(;\s)+\)').sub('\)', paragraph)
            #paragraph = re.compile('\((;\s)+').sub('\(', paragraph)
            #paragraph = re.compile('(\s;)+\)').sub('\)', paragraph)
            #paragraph = re.compile('\((\s;)+').sub('\(', paragraph)
            #paragraph = re.compile('\s\(\)').sub('', paragraph)
            paragraph = re.compile('(\n\s)+').sub(' ', paragraph)
            paragraph = re.compile('([\t\n]+)|(\s\s)|((\n(\s))+)').sub(' ', paragraph)
            paragraph = re.compile('(\s\s)+').sub(' ', paragraph)
            paragraph = re.compile('(\s\s)+').sub(' ', paragraph)
            paragraph_list.append(paragraph)
        except: pass
    return paragraph_list