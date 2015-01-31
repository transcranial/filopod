# process and add J Neurosci review papers
import parser_BrainRev as parser # can use same parser

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
    
    # PMIDs J Neurosci review articles from 2003/01 to 2013/01
    PMIDs = ['23785162', '23785136', '23238709', '23223276', '23055482', '23055481', '23055480', '23055479', '23055478', '23055477', '23055476', '23055475', '23055474', '23055473', '23055472', '23015425', '23015424', '23015423', '23015421', '22956821', '22573664', '22396398', '22323704', '22072665', '22072664', '22072663', '22072662', '22072661', '22072660', '22072659', '22072658', '22072657', '22072656', '22072655', '21976489', '21900574', '21632916', '21273400', '21248101', '21159947', '21159946', '21147979', '21084591', '21068304', '21068303', '21068302', '21068301', '21068300', '21068299', '21068298', '21068297', '21068296', '21068295', '21068294', '21068293', '21048116', '20810875', '20445041', '20371802', '20371801', '20237256', '20237255', '20219988', '20181578', '20181577', '19923272', '19889985', '19828796', '19828795', '19828794', '19828793', '19828792', '19828791', '19828790', '19828789', '19828788', '19828787', '19828786', '19793961', '19793960', '19726635', '19692592', '19587268', '19571120', '19535573', '19494133', '19494132', '19474304', '19474303', '19458210', '19458209', '19420239', '19420238', '19403804', '19403803', '19386900', '19386899', '19357260', '19339592', '19295140', '19279236', '19244507', '19211866', '19158285', '19144830', '19129378', '19074009', '19052193', '19020008', '19005048', '19005047', '19005046', '19005045', '19005044', '19005043', '19005042', '19005041', '19005040', '19005039', '19005038', '19005037', '19005036', '19005035', '18971452', '18945885', '18829947', '18799666', '18799665', '18784288', '18784287', '18768679', '18768678', '18753365', '18753364', '18701676', '18701675', '18667604', '18632928', '18632927', '18579726', '18524890', '18480269', '18434506', '18434505', '18417690', '18417689', '18337397', '18337396', '18322076', '18287494', '18234879', '18199757', '18160630', '18094228', '18057193', '18057192', '18032647', '18032646', '18003821', '18003820', '17989277', '17989276', '17978026', '17978025', '17978024', '17978023', '17978022', '17978021', '17978020', '17978019', '17978018', '17978017', '17978016', '17978015', '17978014', '17959787', '17959786', '17942711', '17942710', '17928433', '17928432', '17913898', '17913897', '17881513', '17855596', '17670964', '17670963', '17670962', '17670961', '17670960', '17670959', '17670957', '17611260', '17581947', '17567795', '17553980', '17553979', '17537954', '17537953', '17522298', '17507549', '17507548', '17460062', '17460061', '17442806', '17428966', '17409225', '17392451', '17304703', '17304702', '17274117', '17274116', '17256187', '17240549', '17205618', '17193727', '17186625', '17171827', '17152680', '17139795', '17128515', '17106946', '17083164', '17083163', '17068864', '17068863', '17058328', '17050702', '17050701', '17050700', '17050699', '17039615', '17035522', '17035521', '17035520', '17035519', '17035518', '17035517', '17035516', '17035515', '16826635', '16826634', '16822971', '16822970', '16822969', '16822968', '16822967', '16822966', '16807320', '16807319', '16467514', '16467513', '16291931', '16280578', '16280577', '16280576', '16280575', '16280574', '16280573', '16280572', '16280571', '16280570', '16267212', '16237160', '16148218', '15496660', '15496659', '15496658', '15496657', '15496656', '15496655', '15496654', '15496653', '15456813', '15456812', '15456811', '15456810', '15456809', '12764085', '12764084', '12764083', '12764082', '12764081', '12764080', '12764079']
    for count, PMID in enumerate(PMIDs):
        url = 'http://www.jneurosci.org/cgi/pmidlookup?view=long&pmid=%s' % PMID
        try:
            sys.stdout.write("article # " + str(count) + " reading url...")
            start = time()
            r = br.open(url)
            entry_url = r.geturl()
            entry_html_source = r.read()
            soup = BeautifulSoup(entry_html_source.decode('utf-8'), 'html5lib')
            is_free = soup.find(class_='free-full-text')
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
                res_metadata[1] = 'J of Neuroscience'
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
                        name = figure[0],
                        type = 'figure',
                        content = figure[1],
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
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    sys.stdout.write("~~~~loading concepts and term lists... ")
    start = time()
    file = open('scripts\MESH_concept_and_terms_tuple.pkl','rb')
    (tot_concepts, concept_IDs, term_lists) = pickle_zloads(file.read())
    file.close()
    sys.stdout.write("%.2f" % (time()-start) + "seconds\n")
    sys.stdout.flush()
    
    res_ids = list(Resource.objects.filter(type="J of Neuroscience").values_list('id',flat=True))
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
    
    bigA_AtA_sentence_path = 'matrices/JNeurosciRev_bigA_AtA_sentence.pkl'
    bigA_AtA_sentence_file = default_storage.open(bigA_AtA_sentence_path,'wb')
    mf = MatrixFiles(name='J of Neuroscience', type='AtA_sentence', path=bigA_AtA_sentence_path)
    mf.save()
    mf.user.add(9) # corresponds to admin@filopod.com
    bigA_AtA_sentence_tuple = (bigA_AtA_sentence, N_sentence)
    bigA_AtA_sentence_file.write(pickle_zdumps(bigA_AtA_sentence_tuple))
    bigA_AtA_sentence_file.close()
    
    #bigA_AtA_paragraph_path = 'matrices/JNeurosciRev_bigA_AtA_paragraph.pkl'
    #bigA_AtA_paragraph_file = default_storage.open(bigA_AtA_paragraph_path,'wb')
    #mf = MatrixFiles(name='J of Neuroscience', type='AtA_paragraph', path=bigA_AtA_paragraph_path)
    #mf.save()
    #mf.user.add(9) # corresponds to admin@filopod.com
    #bigA_AtA_paragraph_tuple = (bigA_AtA_paragraph, N_paragraph)
    #bigA_AtA_paragraph_file.write(pickle_zdumps(bigA_AtA_paragraph_tuple))
    #bigA_AtA_paragraph_file.close()
    
    sys.stdout.write("......" + str(time()-start) + " seconds\n")
    sys.stdout.flush()