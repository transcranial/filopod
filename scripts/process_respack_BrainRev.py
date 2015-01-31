# process and add Brain review papers
import parser_BrainRev as parser

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
    
    # PMIDs Brain review articles from 2003/01 to 2013/01
    PMIDs = ['23365091', '23107648', '22975391', '22961543', '22734127', '22661746', '22577217', '22427329', '22382359', '22366790', '22344583', '22334584', '22171351', '22067541', '22036961', '21933808', '21914716', '21810889', '21624926', '21507994', '21414995', '21378098', '21278084', '21257651', '21247931', '21147837', '21126993', '21030432', '20846944', '20639545', '20584945', '20584944', '20584943', '20472654', '20403960', '20375131', '20354001', '20194141', '20176575', '20150322', '20129937', '20047903', '19933510', '19917643', '19903731', '19892768', '19773354', '19690094', '19617196', '19587129', '19578124', '19506071', '19443629', '19336464', '19336460', '19321463', '19297505', '19251757', '19098031', '19022857', '18971203', '18952673', '18819990', '18790819', '18728095', '18718967', '18684770', '18669495', '18586760', '18567924', '18567623', '18558616', '18515323', '18490360', '18474520', '18292080', '18234698', '18222990', '18202104', '18187492', '18084012', '18055494', '18055491', '18048446', '17967805', '17947337', '17940085', '17932100', '17898008', '17785346', '17715141', '17711979', '17626033', '17575281', '17550907', '17535834', '17533170', '17478443', '17470497', '17438015', '17412731', '17392317', '17353225', '17347254', '17337484', '17322562', '17264093', '17242025', '17138570', '17132643', '17124190', '17121745', '17121742', '17071919', '17018549', '17012295', '17008335', '17003072', '16921175', '16845129', '16816391', '16803839', '16803834', '16738059', '16672292', '16670178', '16636022', '16632554', '16613893', '16597654', '16549399', '16399806', '16371409', '16317026', '16317025', '16254018', '16230322', '16230321', '16195245', '16195244', '16141282', '16049041', '15975943', '15930045', '15901648', '15872015', '15845632', '15758038', '15758032', '15743870', '15728654', '15713848', '15689357', '15649952', '15574465', '15492113', '15358637', '15329353', '15329351', '15215212', '15180926', '15090473', '15090471', '15047588', '14724127', '14711881', '14645147', '14607789', '14607787', '12958081', '12902310', '12847080', '12847079', '12847074', '12805099', '12805098', '12805097', '12764049', '12690044', '12615636', '12566274', '12477701', '12477693']
    for count, PMID in enumerate(PMIDs[34:]):
        url = 'http://brain.oxfordjournals.org/cgi/pmidlookup?view=long&pmid=%s' % PMID
        try:
            sys.stdout.write("article # " + str(count) + " reading url...")
            limitReached = True
            while True:
                if not limitReached:
                    break
                try:
                    start = time()
                    r = br.open(url)
                    limitReached = False
                except:
                    limitReached = True
                    sys.stdout.write("error or limit reached, waiting...")
                    sleep(7200)
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
                res_metadata[1] = 'Brain'
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
    
    res_ids = list(Resource.objects.filter(type="Brain").values_list('id',flat=True))
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
    
    bigA_AtA_sentence_path = 'matrices/BrainRev_bigA_AtA_sentence.pkl'
    bigA_AtA_sentence_file = default_storage.open(bigA_AtA_sentence_path,'wb')
    mf = MatrixFiles(name='Brain', type='AtA_sentence', path=bigA_AtA_sentence_path)
    mf.save()
    mf.user.add(9) # corresponds to admin@filopod.com
    bigA_AtA_sentence_tuple = (bigA_AtA_sentence, N_sentence)
    bigA_AtA_sentence_file.write(pickle_zdumps(bigA_AtA_sentence_tuple))
    bigA_AtA_sentence_file.close()
    
    #bigA_AtA_paragraph_path = 'matrices/BrainRev_bigA_AtA_paragraph.pkl'
    #bigA_AtA_paragraph_file = default_storage.open(bigA_AtA_paragraph_path,'wb')
    #mf = MatrixFiles(name='Brain', type='AtA_paragraph', path=bigA_AtA_paragraph_path)
    #mf.save()
    #mf.user.add(9) # corresponds to admin@filopod.com
    #bigA_AtA_paragraph_tuple = (bigA_AtA_paragraph, N_paragraph)
    #bigA_AtA_paragraph_file.write(pickle_zdumps(bigA_AtA_paragraph_tuple))
    #bigA_AtA_paragraph_file.close()
    
    sys.stdout.write("......" + str(time()-start) + " seconds\n")
    sys.stdout.flush()