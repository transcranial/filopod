# process and add Pediatrics review papers
import parser_Pediatrics as parser

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
    
    # volume/page of Pediatrics review articles from 2003/01 to 2013/01
    PMIDs = ['23184113', '23184107', '23184103', '23166346', '23166341', '23118260', '23118243', '23118242', '23129072', '23118140', '23071205', '23045562', '23045554', '23027174', '23008452', '22945412', '22926181', '22926176', '22926172', '22926170', '22891222', '22869825', '22661762', '22661761', '22661760', '22661759', '22661758', '22661757', '22661756', '22826576', '22778309', '22778306', '22753552', '22732171', '22711727', '22661763', '22665408', '22665407', '22641765', '22641763', '22641762', '22641759', '22614768', '22566424', '22473374', '22473366', '22451713', '22451712', '22451708', '22451705', '22430458', '22430451', '22430448', '22392183', '22392170', '22371471', '22371468', '22351894', '22351885', '22351884', '22300827', '22331340', '22331338', '22311996', '22232312', '22232307', '22201152', '22201146', '22157133', '22144705', '22123880', '22123870', '22106073', '22065270', '22042818', '22042817', '22042816', '22025595', '22007004', '22007003', '22007002', '21987705', '21987696', '21969285', '21949142', '21949139', '21930554', '21930548', '21885648', '21873700', '21873697', '21873692', '21859916', '21859912', '21824877', '21788218', '21788215', '21768324', '21768321', '21746727', '21727101', '21669896', '21646264', '21646259', '21646256', '21624885', '21624884', '21624882', '21624876', '21606151', '21576310', '21576306', '21536618', '21536616', '21518722', '21518720', '21518712', '21518710', '21502251', '21502249', '21502248', '21502242', '21502240', '21482600', '21464196', '21464193', '21464191', '21464190', '21464188', '21464183', '21444591', '21357346', '21357345', '21357342', '21357336', '21357332', '21339266', '21321035', '21321033', '21321027', '21321023', '21285335', '21282269', '21262891', '21220405', '21220400', '21220391', '21199855', '21199853', '21199851', '21173004', '21149435', '21149424', '21123475', '21123473', '21135001', '21115585', '21115584', '21115583', '21098156', '21059720', '21059717', '21041285', '20974781', '20956434', '20956433', '20956432', '20956431', '20956430', '20937658', '20921071', '20921070', '20921069', '20921068', '20876176', '20837588', '20819896', '20696732', '20696726', '20679313', '20679304', '20679303', '20603260', '20566617', '20566606', '20547645', '20530073', '20498174', '20498167', '20498166', '20478944', '20478936', '20421261', '20421259', '20421258', '20403938', '20403936', '20403930', '20368325', '20351005', '20351003', '20351000', '20308212', '20308210', '20308209', '20231186', '20231182', '20194281', '20194279', '20194275', '20176672', '20176665', '20156901', '20142293', '20048084', '20048083', '20123765', '20100768', '20083531', '20083519', '20083517', '19933727', '19917586', '19901005', '19861481', '19861480', '19861475', '19861474', '19861471', '19861470', '19861469', '19861468', '19841113', '19786458', '19786457', '19786456', '19786455', '19786454', '19786452', '19786450', '19786436', '19770174', '19752082', '19720672', '19720668', '19736267', '19736263', '19706577', '19706568', '19651590', '19651589', '19564322', '19564261', '19482769', '19482768', '19470608', '19470607', '19470600', '19451190', '19420154', '19420151', '19420150', '19420149', '19420148', '19420146', '19403506', '19221164', '19336382', '19336381', '19336380', '19336379', '19336362', '19336361', '19332438', '19255042', '19254986', '19221154', '19171629', '19117909', '19117908', '19117907', '19117905', '19117904', '19117903', '19117880', '19117879', '19117878', '19117877', '19117870', '19117869', '19117862', '19117838', '19047263', '19047262', '19047261', '19047255', '19047254', '19047228', '19047227', '19047226', '19015205', '19001038', '18978010', '18978009', '18978008', '18978007', '18978006', '18978005', '18977992', '18977991', '18829818', '18829817', '18829816', '18829815', '18829814', '18829813', '18829812', '18829811', '18829810', '18829809', '18829808', '18829807', '18829806', '18829788', '18809596', '18762538', '18762536', '18762535', '18762533', '18762528', '18762512', '18762511', '18678603', '18676567', '18676559', '18676536', '18676506', '18662935', '18596007', '18596006', '18595997', '18595996', '18595973', '18519492', '18519458', '18450914', '18450888', '18450883', '18443019', '18381498', '18381497', '18381496', '18381495', '18381494', '18381493', '18381492', '18381552', '18381551', '18381550', '18381549', '18381546', '18381529', '18381527', '18381526', '18381525', '18381500', '18381499', '18378549', '18310216', '18310215', '18310210', '18310209', '18310208', '18310207', '18310191', '18310190', '18245514', '18245513', '18245512', '18245511', '18245510', '18245429', '18245428', '18245427', '18245410', '18245409', '18245408', '18174323', '18174317', '18187811', '18166574', '18166571', '18166570', '18166538', '18055654', '18055653', '18055652', '18055691', '18055690', '18055686', '18055684', '18055683', '18055670', '18055668', '17974754', '17974753', '17974752', '17974750', '17974749', '17974748', '17974747', '17974746', '17974726', '17974725', '17974724', '17974723', '17974721', '17967924', '17967923', '17967922', '17967921', '17967920', '17908773', '17908772', '17908771', '17908730', '17908729', '17767009', '17767008', '17767007', '17767006', '17766534', '17724112', '17671070', '17671069', '17671068', '17671048', '17671047', '17603094', '17606543', '17545398', '17545397', '17545395', '17545394', '17545393', '17545392', '17545391', '17545390', '17545389', '17545388', '17545387', '17545368', '17545366', '17545365', '17533177', '17515437', '17473106', '17473105', '17473104', '17473102', '17473101', '17473100', '17473099', '17473098', '17473085', '17470565', '17403862', '17403859', '17403856', '17403855', '17403854', '17403853', '17403852', '17403851', '17403850', '17403849', '17332238', '17332236', '17332221', '17332211', '17332209', '17332208', '17332207', '17325213', '17272627', '17242136', '17242135', '17200279', '17200278', '17200277', '17178922', '17142557', '17142508', '17142507', '17079600', '17079590', '17079589', '17079575', '17030599', '17015562', '17015493', '17000783', '16982808', '16966391', '16960984', '16951031', '16951027', '16951018', '16951016', '16951015', '16950972', '16950946', '16882833', '16882832', '16882822', '16882788', '16882787', '16880251', '16864641', '16818584', '16818581', '16818580', '16818579', '16816003', '16740881', '16740880', '16740869', '16740868', '16740851', '16740823', '16740821', '16651334', '16651333', '16606681', '16585335', '16585334', '16585299', '16585290', '16567392', '16510634', '16452368', '16452337', '16452336', '16452335', '16396876', '16361223', '16322180', '16322167', '16263987', '16199712', '16140720', '16061606', '16061583', '16001458', '15995055', '15995013', '15930245', '15930239', '15930238', '15930231', '15930229', '15930212', '15930203', '15930202', '15930200', '15930199', '15867051', '15867049', '15867026', '15866863', '15866854', '15805390', '15805383', '15741383', '15741382', '15741381', '15741380', '15741363', '15629961']
    for count, PMID in enumerate(PMIDs):
        url = 'http://pediatrics.aappublications.org/cgi/pmidlookup?view=long&pmid=%s' % PMID
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
                res_metadata[1] = 'Pediatrics'
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
    
    res_ids = list(Resource.objects.filter(type="Pediatrics").values_list('id',flat=True))
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
    
    bigA_AtA_sentence_path = 'matrices/PediatricsRev_bigA_AtA_sentence.pkl'
    bigA_AtA_sentence_file = default_storage.open(bigA_AtA_sentence_path,'wb')
    mf = MatrixFiles(name='Pediatrics', type='AtA_sentence', path=bigA_AtA_sentence_path)
    mf.save()
    mf.user.add(9) # corresponds to admin@filopod.com
    bigA_AtA_sentence_tuple = (bigA_AtA_sentence, N_sentence)
    bigA_AtA_sentence_file.write(pickle_zdumps(bigA_AtA_sentence_tuple))
    bigA_AtA_sentence_file.close()
    
    #bigA_AtA_paragraph_path = 'matrices/PediatricsRev_bigA_AtA_paragraph.pkl'
    #bigA_AtA_paragraph_file = default_storage.open(bigA_AtA_paragraph_path,'wb')
    #mf = MatrixFiles(name='Pediatrics', type='AtA_paragraph', path=bigA_AtA_paragraph_path)
    #mf.save()
    #mf.user.add(9) # corresponds to admin@filopod.com
    #bigA_AtA_paragraph_tuple = (bigA_AtA_paragraph, N_paragraph)
    #bigA_AtA_paragraph_file.write(pickle_zdumps(bigA_AtA_paragraph_tuple))
    #bigA_AtA_paragraph_file.close()
    
    sys.stdout.write("......" + str(time()-start) + " seconds\n")
    sys.stdout.flush()