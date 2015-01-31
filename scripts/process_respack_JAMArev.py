# process and add JAMA review papers
import parser_JAMA as parser

import mechanize
import cookielib
from bs4 import BeautifulSoup
from time import time
from time import sleep
from random import randint
import sys
import cPickle as pickle
import zlib
from main.models import *
from nltk.tokenize import sent_tokenize
from scipy.sparse import coo_matrix, csr_matrix, vstack
from scipy import int16
from numpy import array
import re2
from django.core.files.storage import default_storage
import uuid
import traceback

'''pickle and compress obj'''
def pickle_zdumps(obj):
    return zlib.compress(pickle.dumps(obj,pickle.HIGHEST_PROTOCOL),9)

'''unpickle and decompress obj'''
def pickle_zloads(zstr):
    return pickle.loads(zlib.decompress(zstr))

def run():

    '''
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    start = time()
    # Browser
    br = mechanize.Browser()
    # Cookie Jar
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)
    # Browser options
    br.set_handle_equiv(True)
    #br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)
    # Follows refresh 0 but not hangs on refresh > 0
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
    # Want debugging messages?
    #br.set_debug_http(True)
    #br.set_debug_redirects(True)
    #br.set_debug_responses(True)
    # User-Agent
    br.addheaders = [('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11')]
    print "initiated browser: " + str(time()-start) + " seconds"
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    # volume/page of JAMA review articles from 2000/01 to 2013/04/1
    vol_pg_tuples = [('309', '1278'), ('309', '1163'), ('309', '926'), ('309', '919'), ('309', '814'), ('309', '706'), ('309', '678'), ('309', '594'), ('308', '2507'), ('309', '71'), ('308', '2612'), ('308', '1024'), ('308', '502'), ('307', '2526'), ('307', '2079'), ('307', '2418'), ('307', '1959'), ('307', '1185'), ('307', '1072'), ('307', '713'), ('307', '294'), ('307', '182'), ('306', '2704'), ('306', '2011'), ('306', '1782'), ('306', '1688'), ('306', '1359'), ('306', '1241'), ('306', '978'), ('306', '746'), ('306', '627'), ('306', '420'), ('305', '2335'), ('305', '1790'), ('305', '1327'), ('305', '1225'), ('305', '1119'), ('305', '1008'), ('305', '698'), ('305', '487'), ('305', '284'), ('305', '78'), ('304', '2628'), ('304', '2161'), ('304', '2048'), ('304', '1592'), ('304', '890'), ('304', '779'), ('304', '452'), ('304', '321'), ('304', '76'), ('303', '2280'), ('303', '1848'), ('303', '1738'), ('303', '1729'), ('303', '1526'), ('303', '1295'), ('303', '1180'), ('303', '1077'), ('303', '865'), ('303', '438'), ('303', '47'), ('302', '2679'), ('302', '2345'), ('302', '2243'), ('302', '2135'), ('302', '1316'), ('302', '985'), ('302', '550'), ('302', '537'), ('302', '412'), ('302', '179'), ('301', '2472'), ('301', '2362'), ('301', '2349'), ('302', '73'), ('301', '2129'), ('301', '1358'), ('301', '636'), ('301', '954'), ('301', '415'), ('301', '309'), ('300', '2886'), ('300', '2779'), ('300', '2754'), ('300', '2647'), ('300', '2638'), ('300', '2514'), ('301', '82'), ('300', '2407'), ('300', '2286'), ('300', '2277'), ('300', '2161'), ('300', '1793'), ('300', '1674'), ('300', '2036'), ('300', '1439'), ('300', '1181'), ('300', '711'), ('300', '555'), ('300', '197'), ('299', '2777'), ('299', '2423'), ('299', '1937'), ('299', '1698'), ('299', '1446'), ('299', '1320'), ('299', '1166'), ('299', '937'), ('299', '925'), ('299', '914'), ('299', '806'), ('299', '793'), ('299', '672'), ('299', '324'), ('299', '555'), ('298', '2895'), ('298', '2654'), ('298', '2296'), ('298', '2171'), ('298', '1911'), ('298', '1900'), ('298', '1429'), ('298', '1312'), ('298', '1300'), ('298', '1038'), ('298', '1023'), ('298', '902'), ('298', '786'), ('298', '655'), ('298', '438'), ('298', '194'), ('298', '70'), ('298', '61'), ('297', '2741'), ('297', '2617'), ('297', '2603'), ('297', '2502'), ('297', '2391'), ('297', '2381'), ('297', '2264'), ('297', '2251'), ('297', '2241'), ('297', '2018'), ('297', '1810'), ('297', '1697'), ('297', '1583'), ('297', '1551'), ('297', '1478'), ('297', '1241'), ('297', '1233'), ('297', '986'), ('297', '842'), ('297', '831'), ('297', '733'), ('297', '724'), ('297', '77'), ('296', '2839'), ('296', '2558'), ('296', '2234'), ('296', '2012'), ('296', '1885'), ('296', '1764'), ('296', '1731'), ('296', '1507'), ('296', '1377'), ('296', '1274'), ('296', '1619'), ('296', '1633'), ('296', '1116'), ('296', '1103'), ('296', '1094'), ('296', '974'), ('296', '815'), ('296', '679'), ('296', '445'), ('296', '427'), ('295', '2765'), ('295', '2286'), ('295', '2275'), ('295', '2057'), ('295', '1824'), ('295', '1688'), ('295', '1566'), ('295', '1288'), ('295', '1050'), ('295', '809'), ('295', '547'), ('295', '536'), ('295', '416'), ('295', '403'), ('295', '199'), ('294', '3124'), ('294', '2889'), ('294', '2751'), ('294', '2623'), ('294', '2342'), ('294', '2203'), ('294', '2064'), ('294', '1944'), ('287', '2784'), ('284', '1417'), ('287', '1301'), ('289', '3161'), ('289', '1976'), ('291', '2865'), ('294', '947'), ('289', '217'), ('285', '2498'), ('288', '2793'), ('289', '331'), ('285', '1819'), ('291', '2013'), ('293', '3043'), ('293', '1509'), ('292', '972'), ('289', '1837'), ('289', '2992'), ('283', '2568'), ('286', '1610'), ('292', '726'), ('292', '1593'), ('287', '2701'), ('288', '2151'), ('284', '2919'), ('289', '3145'), ('287', '2335'), ('290', '1001'), ('294', '725'), ('289', '747'), ('293', '730'), ('283', '1451'), ('284', '1820'), ('285', '1415'), ('287', '2570'), ('285', '1613'), ('287', '2869'), ('284', '2785'), ('290', '1360'), ('285', '3065'), ('293', '2391'), ('291', '2367'), ('288', '1388'), ('293', '1906'), ('284', '215'), ('293', '1089'), ('287', '1233'), ('286', '208'), ('291', '870'), ('284', '934'), ('290', '248'), ('291', '358'), ('287', '1840'), ('293', '855'), ('292', '1989'), ('294', '97'), ('285', '193'), ('288', '1116'), ('292', '2890'), ('293', '90'), ('289', '1288'), ('291', '1610'), ('290', '2599'), ('287', '1502'), ('294', '1088'), ('289', '1681'), ('292', '1480'), ('288', '2579'), ('293', '2372'), ('288', '611'), ('291', '99'), ('286', '2516'), ('291', '986'), ('290', '86'), ('283', '381'), ('285', '2763'), ('287', '487'), ('287', '883'), ('283', '3110'), ('287', '1308'), ('293', '596'), ('292', '1602'), ('293', '1245'), ('293', '2012'), ('293', '1644'), ('286', '1360'), ('288', '1889'), ('291', '228'), ('286', '2787'), ('285', '1489'), ('287', '226'), ('294', '1534'), ('292', '852'), ('286', '1218'), ('288', '3137'), ('290', '2464'), ('288', '2233'), ('291', '2359'), ('289', '2475'), ('293', '979'), ('287', '1848'), ('290', '524'), ('293', '1653'), ('290', '932'), ('283', '1469'), ('292', '2755'), ('286', '2308'), ('287', '622'), ('291', '1999'), ('287', '2414'), ('287', '1022'), ('285', '1059'), ('293', '2141'), ('287', '425'), ('289', '2254'), ('291', '1887'), ('293', '987'), ('287', '2691'), ('286', '2143'), ('289', '2857'), ('293', '1223'), ('292', '367'), ('288', '932'), ('285', '1338'), ('285', '2891'), ('294', '238'), ('293', '1501'), ('292', '1724'), ('286', '895'), ('293', '477'), ('290', '1767'), ('292', '1867'), ('292', '2901'), ('290', '659'), ('291', '2746'), ('289', '589'), ('289', '347'), ('286', '341'), ('291', '605'), ('287', '1972'), ('283', '2008'), ('283', '3244'), ('289', '210'), ('288', '2868'), ('286', '2000'), ('293', '2641'), ('288', '2569'), ('291', '1127'), ('284', '412'), ('292', '2880'), ('286', '2296'), ('286', '3056'), ('288', '2167'), ('288', '872'), ('285', '1193'), ('285', '992'), ('289', '2413'), ('287', '1435'), ('285', '2055'), ('292', '97'), ('286', '1149'), ('292', '1074'), ('291', '1238'), ('291', '1368'), ('290', '2849'), ('290', '2057'), ('288', '2458'), ('285', '2232'), ('286', '442'), ('288', '629'), ('290', '2455'), ('288', '1901'), ('287', '2114'), ('288', '2724'), ('289', '80'), ('284', '1689'), ('289', '3300'), ('292', '2874'), ('291', '2243'), ('292', '89'), ('287', '92'), ('293', '1367'), ('289', '2545'), ('290', '1633'), ('287', '762'), ('288', '2449'), ('292', '2771'), ('290', '2301'), ('290', '1510'), ('285', '1186'), ('283', '3102'), ('285', '785'), ('291', '736'), ('292', '237'), ('292', '2622'), ('290', '1906'), ('289', '2041'), ('285', '1987'), ('289', '2120'), ('290', '2476'), ('284', '1549'), ('294', '1671'), ('286', '2270'), ('287', '2391'), ('283', '2281'), ('286', '2981'), ('293', '2257'), ('287', '360'), ('283', '1800'), ('286', '2441'), ('289', '2849'), ('287', '2120'), ('289', '895'), ('292', '490'), ('288', '1622'), ('293', '217'), ('287', '236'), ('291', '350'), ('291', '1487'), ('287', '2917'), ('286', '944'), ('286', '821'), ('288', '745'), ('288', '222'), ('287', '2236'), ('293', '349'), ('292', '2388'), ('287', '628'), ('285', '386'), ('287', '2821'), ('284', '1828'), ('286', '954'), ('291', '1763'), ('292', '3017'), ('288', '351'), ('289', '454'), ('288', '1610'), ('287', '3116'), ('290', '719')]
    for count, vol_pg_tuple in enumerate(vol_pg_tuples):
        url = 'http://jama.jamanetwork.com/article.aspx?volume=%s&page=%s' % vol_pg_tuple
        try:
            sys.stdout.write("article # " + str(count) + " reading url...")
            start = time()
            r = br.open(url)
            entry_url = r.geturl()
            entry_html_source = r.read()
            soup = BeautifulSoup(entry_html_source.decode('utf-8'), 'html5lib')
            is_free = soup.find(class_='freeArticle')
            if is_free is None:
                sys.stdout.write(str(time()-start) + " seconds")
                sys.stdout.write("...skipping, article not free.\n")
                sys.stdout.flush()
            else:
                sys.stdout.write("adding to database...")
                # format of returned list from get_metadata function:
                # 0 identifier
                # 1 type
                # 2 language
                # 3 title
                # 4 date
                # 5 publisher
                # 6 author
                # 7 journal
                # 8 volume
                # 9 issue
                # 10 firstpage
                # 11 lastpage
                # 12 url
                res_metadata = parser.get_metadata(entry_url, entry_html_source)
                res_metadata[1] = 'JAMA review articles'
                res_identifier = res_metadata[0]
                # creates new Resource object and containing Subresource objects
                # creates Resource based on returned parser metadata
                res = Resource(identifier = res_metadata[0],
                    type = res_metadata[1],
                    language = res_metadata[2],
                    title = res_metadata[3],
                    date = res_metadata[4],
                    publisher = res_metadata[5],
                    author = res_metadata[6],
                    journal = res_metadata[7],
                    volume = res_metadata[8],
                    issue = res_metadata[9],
                    firstpage = res_metadata[10],
                    lastpage = res_metadata[11],
                    url = entry_url,
                    html_source = entry_html_source)
                res.save()
                res.user.add(9) # corresponds to admin@filopod.com
                #res.user.add(2) # corresponds to lchen3@gmail.com
                res.domain.add(1) # corresponds to Biomedical
                subres = []
                # creates Subresource objects of type 'figure'
                figures = parser.get_figures(entry_url, entry_html_source)
                for i, figure in enumerate(figures):
                    subres.append(Subresource(containing_resource = res,
                        name = figure[0].split('. ')[0],
                        type = 'figure',
                        content = u'. '.join(figure[0].split('. ')[1:]) + u'. ' + figure[1],
                        url = figure[4]))
                # creates Subresource objects of type 'paragraph'
                paragraphs = parser.get_paragraphs(entry_url, entry_html_source)
                for i, paragraph in enumerate(paragraphs):
                    subres.append(Subresource(containing_resource = res,
                        name = 'paragraph ' + str(i),
                        type = 'paragraph',
                        content = paragraph))
                subres_temp = Subresource.objects.bulk_create(subres)
                del subres_temp
                del subres
                sys.stdout.write(str(time()-start) + " seconds\n")
                sys.stdout.flush()
        except Exception, e:
            print "failed. exception: "+str(e)
            traceback.print_exc()
    '''
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    sys.stdout.write("~~~~loading concepts and term lists... ")
    start = time()
    file = open('scripts\MESH_concept_and_terms_tuple.pkl','rb')
    (tot_concepts, concept_IDs, term_lists) = pickle_zloads(file.read())
    file.close()
    sys.stdout.write("%.2f" % (time()-start) + "seconds\n")
    sys.stdout.flush()
    
    res_ids = list(Resource.objects.filter(type="JAMA review articles").values_list('id',flat=True))
    print "total # of resources: " + str(len(res_ids))
    for count, res_id in enumerate(res_ids):        
        try:
            sys.stdout.write("article # " + str(count) + " processing...")
            start = time()
            target_paragraphs = Subresource.objects.filter(containing_resource_id=res_id)
            
            #create sentences from target_paragraphs
            sentences = []
            sentences_indexofparagraph = []
            tot_para = 0
            tot_sent = 0
            for para_num, target_paragraph in enumerate(target_paragraphs):
                #find all sentence in this paragraph
                tokenized_sentences = sent_tokenize(target_paragraph.content.rstrip())
                sentences.extend(tokenized_sentences)
                sentences_indexofparagraph.extend([para_num]*len(tokenized_sentences))
                tot_sent = tot_sent + len(tokenized_sentences)
                tot_para = tot_para + 1
            tot_para = len(target_paragraphs)
            
            #second go through each concept/term, find them in subresources, and process into matrix
            tc = 0
            j = 0
            row_sentence = []
            row_paragraph = []
            col_sentence = []
            col_paragraph = []
            data_sentence = []
            data_paragraph = []
            # initialize list of empty lists for storing concepts contained in each paragraph
            para_conceptIDs_contained = [[] for i in range(tot_para)]
            for i, con_ID in enumerate(concept_IDs):
                term_list = term_lists[i]
                wordcount_in_paragraphs = [0] * tot_para
                terms_regex = [r"\b"+re2.escape(term.lower())+r"\b" for term in term_list]
                search_pattern = re2.compile("|".join(terms_regex))
                for sent_num, sentence in enumerate(sentences):
                    wordcount = len(search_pattern.findall(sentence.lower()))
                    if wordcount > 0: #only go ahead if search_pattern is in the sentence
                        row_sentence.append(sent_num)
                        col_sentence.append(tc)
                        data_sentence.append(1)
                        wordcount_in_paragraphs[sentences_indexofparagraph[sent_num]] += wordcount
                for para_num in range(tot_para):
                    wordcount_in_p = wordcount_in_paragraphs[para_num]
                    if wordcount_in_p > 0:
                        row_paragraph.append(para_num)
                        col_paragraph.append(tc)
                        data_paragraph.append(1)
                        para_conceptIDs_contained[para_num].append(con_ID)
                if tc*10/tot_concepts > j:
                    percent_done = tc*10/tot_concepts*10
                    sys.stdout.write(str(percent_done) + "% ")
                    j=j+1
                tc = tc + 1
            
            # update concepts_contained fields for all subresource objects
            for para_num in range(tot_para):
                if len(para_conceptIDs_contained[para_num]) > 0:
                    target_paragraphs[para_num].concepts_contained.add(*para_conceptIDs_contained[para_num])
                    
            #create target_A matrix
            target_A_sentence = coo_matrix((array(data_sentence),(array(row_sentence),array(col_sentence))),shape=(tot_sent,tot_concepts),dtype=int16)
            #target_A_paragraph = coo_matrix((array(data_paragraph),(array(row_paragraph),array(col_paragraph))),shape=(tot_para,tot_concepts),dtype=int16)
            
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # now convert target_A into a scipy csr_matrix (sparse matrix)
            target_A_sentence = target_A_sentence.tocsr()
            #target_A_paragraph = target_A_paragraph.tocsr()
            
            # calculate AtA for target_A
            AtA_sentence = target_A_sentence.T * target_A_sentence
            #AtA_paragraph = target_A_paragraph.T * target_A_paragraph
            
            # add AtA to Big_A
            if count==0:
                bigA_AtA_sentence = AtA_sentence
                N_sentence = tot_sent
                #bigA_AtA_paragraph = AtA_paragraph
                #N_paragraph = tot_para
            else:
                bigA_AtA_sentence = bigA_AtA_sentence + AtA_sentence
                N_sentence = N_sentence + tot_sent
                #bigA_AtA_paragraph = bigA_AtA_paragraph + AtA_paragraph
                #N_paragraph = N_paragraph + tot_para
            
            sys.stdout.write(str(time()-start) + " seconds\n")
            sys.stdout.flush()
        except Exception, e:
            print "failed. exception: "+str(e)
            traceback.print_exc()
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    sys.stdout.write("files saving...")
    start = time()
    
    bigA_AtA_sentence_path = 'matrices/JAMArev_bigA_AtA_sentence.pkl'
    bigA_AtA_sentence_file = default_storage.open(bigA_AtA_sentence_path,'wb')
    mf = MatrixFiles(name='JAMA review articles', type='AtA_sentence', path=bigA_AtA_sentence_path)
    mf.save()
    mf.user.add(9) # corresponds to admin@filopod.com
    bigA_AtA_sentence_tuple = (bigA_AtA_sentence, N_sentence)
    bigA_AtA_sentence_file.write(pickle_zdumps(bigA_AtA_sentence_tuple))
    bigA_AtA_sentence_file.close()
    
    #bigA_AtA_paragraph_path = 'matrices/JAMArev_bigA_AtA_paragraph.pkl'
    #bigA_AtA_paragraph_file = default_storage.open(bigA_AtA_paragraph_path,'wb')
    #mf = MatrixFiles(name='JAMA review articles', type='AtA_paragraph', path=bigA_AtA_paragraph_path)
    #mf.save()
    #mf.user.add(9) # corresponds to admin@filopod.com
    #bigA_AtA_paragraph_tuple = (bigA_AtA_paragraph, N_paragraph)
    #bigA_AtA_paragraph_file.write(pickle_zdumps(bigA_AtA_paragraph_tuple))
    #bigA_AtA_paragraph_file.close()
    
    sys.stdout.write("......" + str(time()-start) + " seconds\n")
    sys.stdout.flush()