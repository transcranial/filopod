# process and add Radiology review papers
import parser_RadioGraphics as parser

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
import urllib2

'''pickle and compress obj'''
def pickle_zdumps(obj):
    return zlib.compress(pickle.dumps(obj,pickle.HIGHEST_PROTOCOL),9)

'''unpickle and decompress obj'''
def pickle_zloads(zstr):
    return pickle.loads(zlib.decompress(zstr))

def run():

    '''#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
    
    # PMIDs and DOIs of Radiology review articles from 2003/01 to 2013/01
    identifiers = [{"pmid":12601205,"doi":"10.1148/radiol.2263011540"},{"pmid":12616012,"doi":"10.1148/radiol.2271001744"},{"pmid":12616015,"doi":"10.1148/radiol.2263020109"},{"pmid":12637675,"doi":"10.1148/radiol.2272011329"},{"pmid":12637677,"doi":"10.1148/radiol.2272012071"},{"pmid":12668742,"doi":"10.1148/radiol.2271010938"},{"pmid":12738874,"doi":"10.1148/radiol.2281020307"},{"pmid":12773666,"doi":"10.1148/radiol.2273011499"},{"pmid":12819343,"doi":"10.1148/radiol.2282011726"},{"pmid":12832569,"doi":"10.1148/radiol.2281020874"},{"pmid":12832573,"doi":"10.1148/radiol.2281021567"},{"pmid":12954885,"doi":"10.1148/radiol.2283030674"},{"pmid":12954888,"doi":"10.1148/radiol.2283021557"},{"pmid":14500855,"doi":"10.1148/radiol.2292030516"},{"pmid":14519867,"doi":"10.1148/radiol.2291020222"},{"pmid":14593188,"doi":"10.1148/radiol.2293010899"},{"pmid":14595138,"doi":"10.1148/radiol.2292020402"},{"pmid":14657300,"doi":"10.1148/radiol.2293031280"},{"pmid":14695382,"doi":"10.1148/radiol.2301031028"},{"pmid":14695386,"doi":"10.1148/radiol.2301021122"},{"pmid":14695395,"doi":"10.1148/radiol.2301021482"},{"pmid":14739312,"doi":"10.1148/radiol.2303021726"},{"pmid":14752175,"doi":"10.1148/radiol.2302031698"},{"pmid":14752178,"doi":"10.1148/radiol.2302021489"},{"pmid":14990813,"doi":"10.1148/radiol.2311020452"},{"pmid":15044750,"doi":"10.1148/radiol.2312021185"},{"pmid":15068942,"doi":"10.1148/radiol.2311021620"},{"pmid":15118110,"doi":"10.1148/radiol.2313021488"},{"pmid":15128979,"doi":"10.1148/radiol.2312032097"},{"pmid":15163803,"doi":"10.1148/radiol.2313040154"},{"pmid":15163813,"doi":"10.1148/radiol.2313030173"},{"pmid":15220490,"doi":"10.1148/radiol.2321021803"},{"pmid":15220491,"doi":"10.1148/radiol.2321030636"},{"pmid":15284429,"doi":"10.1148/radiol.2323031558"},{"pmid":15284433,"doi":"10.1148/radiol.2323030830"},{"pmid":15286305,"doi":"10.1148/radiol.2322021326"},{"pmid":15286311,"doi":"10.1148/radiol.2322040305"},{"pmid":15317956,"doi":"10.1148/radiol.2331020777"},{"pmid":15375227,"doi":"10.1148/radiol.2332031119"},{"pmid":15454614,"doi":"10.1148/radiol.2331041059"},{"pmid":15498896,"doi":"10.1148/radiol.2333031150"},{"pmid":15564389,"doi":"10.1148/radiol.2341031302"},{"pmid":15601895,"doi":"10.1148/radiol.2342031990"},{"pmid":15650038,"doi":"10.1148/radiol.2343030333"},{"pmid":15670993,"doi":"10.1148/radiol.2342030897"},{"pmid":15716389,"doi":"10.1148/radiol.2351031455"},{"pmid":15734922,"doi":"10.1148/radiol.2343041670"},{"pmid":15734925,"doi":"10.1148/radiol.2343031362"},{"pmid":15734929,"doi":"10.1148/radiol.2343031768"},{"pmid":15734940,"doi":"10.1148/radiol.2343030946"},{"pmid":15833981,"doi":"10.1148/radiol.2353040037"},{"pmid":15845798,"doi":"10.1148/radiol.2353042205"},{"pmid":15858079,"doi":"10.1148/radiol.2352040330"},{"pmid":15858080,"doi":"10.1148/radiol.2352040307"},{"pmid":15858081,"doi":"10.1148/radiol.2352040727"},{"pmid":15858087,"doi":"10.1148/radiol.2352040262"},{"pmid":15858096,"doi":"10.1148/radiol.2352032121"},{"pmid":15860674,"doi":"10.1148/radiol.2353040457"},{"pmid":15914473,"doi":"10.1148/radiol.2353041760"},{"pmid":15914474,"doi":"10.1148/radiol.2353041865"},{"pmid":15972340,"doi":"10.1148/radiol.2362040513"},{"pmid":15983074,"doi":"10.1148/radiol.2361041278"},{"pmid":15987959,"doi":"10.1148/radiol.2361041926"},{"pmid":15987960,"doi":"10.1148/radiol.2361031674"},{"pmid":16100082,"doi":"10.1148/radiol.2371040585"},{"pmid":16118165,"doi":"10.1148/radiol.2363041042"},{"pmid":16170017,"doi":"10.1148/radiol.2372050199"},{"pmid":16237143,"doi":"10.1148/radiol.2373041717"},{"pmid":16251391,"doi":"10.1148/radiol.2373040966"},{"pmid":16304103,"doi":"10.1148/radiol.2373050220"},{"pmid":16304111,"doi":"10.1148/radiol.2373050176"},{"pmid":16373757,"doi":"10.1148/radiol.2381041602"},{"pmid":16436808,"doi":"10.1148/radiol.2382051462"},{"pmid":16436809,"doi":"10.1148/radiol.2382041977"},{"pmid":16452394,"doi":"10.1148/radiol.2382050062"},{"pmid":16452395,"doi":"10.1148/radiol.2382050063"},{"pmid":16505391,"doi":"10.1148/radiol.2383041109"},{"pmid":16543592,"doi":"10.1148/radiol.2392050413"},{"pmid":16567481,"doi":"10.1148/radiol.2391041043"},{"pmid":16567482,"doi":"10.1148/radiol.2391050343"},{"pmid":16641348,"doi":"10.1148/radiol.2392052002"},{"pmid":16709793,"doi":"10.1148/radiol.2401050061"},{"pmid":16714455,"doi":"10.1148/radiol.2393042031"},{"pmid":16714456,"doi":"10.1148/radiol.2393050823"},{"pmid":16720868,"doi":"10.1148/radiol.2401050134"},{"pmid":16864664,"doi":"10.1148/radiol.2402050314"},{"pmid":16926320,"doi":"10.1148/radiol.2403050818"},{"pmid":16926321,"doi":"10.1148/radiol.2403050542"},{"pmid":16990669,"doi":"10.1148/radiol.2411050628"},{"pmid":17053199,"doi":"10.1148/radiol.2413051358"},{"pmid":17057062,"doi":"10.1148/radiol.2412060169"},{"pmid":17057063,"doi":"10.1148/radiol.2412041866"},{"pmid":17090716,"doi":"10.1148/radiol.2421052011"},{"pmid":17114619,"doi":"10.1148/radiol.2413051535"},{"pmid":17185659,"doi":"10.1148/radiol.2421052135"},{"pmid":17185660,"doi":"10.1148/radiol.2421051180"},{"pmid":17185662,"doi":"10.1148/radiol.2421050677"},{"pmid":17229874,"doi":"10.1148/radiol.2423051403"},{"pmid":17255408,"doi":"10.1148/radiol.2422051113"},{"pmid":17325062,"doi":"10.1148/radiol.2423051631"},{"pmid":17325078,"doi":"10.1148/radiol.2423041600"},{"pmid":17384237,"doi":"10.1148/radiol.2432050057"},{"pmid":17392247,"doi":"10.1148/radiol.2431030580"},{"pmid":17431128,"doi":"10.1148/radiol.2433060243"},{"pmid":17446526,"doi":"10.1148/radiol.2433061411"},{"pmid":17456864,"doi":"10.1148/radiol.2432060009"},{"pmid":17456865,"doi":"10.1148/radiol.2432060307"},{"pmid":17456883,"doi":"10.1148/radiol.2432030499"},{"pmid":17495176,"doi":"10.1148/radiol.2441052145"},{"pmid":17507723,"doi":"10.1148/radiol.2441060773"},{"pmid":17517922,"doi":"10.1148/radiol.2433070350"},{"pmid":17517924,"doi":"10.1148/radiol.2433060850"},{"pmid":17517925,"doi":"10.1148/radiol.2433051098"},{"pmid":17517926,"doi":"10.1148/radiol.2433051649"},{"pmid":17522346,"doi":"10.1148/radiol.2441051790"},{"pmid":17581895,"doi":"10.1148/radiol.2441051769"},{"pmid":17581896,"doi":"10.1148/radiol.2441060995"},{"pmid":17592037,"doi":"10.1148/radiol.2442060136"},{"pmid":17641360,"doi":"10.1148/radiol.2442051766"},{"pmid":17641361,"doi":"10.1148/radiol.2442051620"},{"pmid":17709823,"doi":"10.1148/radiol.2443060295"},{"pmid":17709824,"doi":"10.1148/radiol.2443051661"},{"pmid":17709825,"doi":"10.1148/radiol.2443060582"},{"pmid":17848679,"doi":"10.1148/radiol.2451061280"},{"pmid":17848685,"doi":"10.1148/radiol.2452070397"},{"pmid":17885179,"doi":"10.1148/radiol.2451060731"},{"pmid":17885180,"doi":"10.1148/radiol.2451051706"},{"pmid":17885181,"doi":"10.1148/radiol.2451051359"},{"pmid":17885185,"doi":"10.1148/radiol.2451061204"},{"pmid":17940297,"doi":"10.1148/radiol.2452061117"},{"pmid":17940298,"doi":"10.1148/radiol.2452061706"},{"pmid":17940300,"doi":"10.1148/radiol.2452060445"},{"pmid":17940301,"doi":"10.1148/radiol.2452061031"},{"pmid":18024448,"doi":"10.1148/radiol.2453060798"},{"pmid":18024449,"doi":"10.1148/radiol.2453061481"},{"pmid":18096524,"doi":"10.1148/radiol.2461061676"},{"pmid":18096526,"doi":"10.1148/radiol.2461061994"},{"pmid":18096527,"doi":"10.1148/radiol.2461061245"},{"pmid":18223119,"doi":"10.1148/radiol.2463061038"},{"pmid":18227534,"doi":"10.1148/radiol.2462071831"},{"pmid":18227535,"doi":"10.1148/radiol.2461070309"},{"pmid":18227536,"doi":"10.1148/radiol.2462061775"},{"pmid":18227540,"doi":"10.1148/radiol.2461070121"},{"pmid":18309012,"doi":"10.1148/radiol.2463060881"},{"pmid":18310461,"doi":"10.1148/radiol.2472061846"},{"pmid":18375837,"doi":"10.1148/radiol.2473061909"},{"pmid":18430871,"doi":"10.1148/radiol.2472061331"},{"pmid":18487532,"doi":"10.1148/radiol.2473062124"},{"pmid":18566164,"doi":"10.1148/radiol.2481080256"},{"pmid":18566166,"doi":"10.1148/radiol.2481072190"},{"pmid":18566168,"doi":"10.1148/radiol.2481071497"},{"pmid":18566169,"doi":"10.1148/radiol.2481060339"},{"pmid":18566177,"doi":"10.1148/radiol.2481071451"},{"pmid":18641243,"doi":"10.1148/radiol.2482070988"},{"pmid":18641245,"doi":"10.1148/radiol.2482062110"},{"pmid":18710972,"doi":"10.1148/radiol.2483070362"},{"pmid":18710973,"doi":"10.1148/radiol.2483062112"},{"pmid":18710974,"doi":"10.1148/radiol.2483071416"},{"pmid":18796665,"doi":"10.1148/radiol.2491070783"},{"pmid":18812557,"doi":"10.1148/radiol.2491071336"},{"pmid":18936309,"doi":"10.1148/radiol.2492071313"},{"pmid":19011181,"doi":"10.1148/radiol.2493070976"},{"pmid":19011184,"doi":"10.1148/radiol.2493080240"},{"pmid":19092089,"doi":"10.1148/radiol.2501071322"},{"pmid":19188309,"doi":"10.1148/radiol.2502081075"},{"pmid":19188310,"doi":"10.1148/radiol.2502071998"},{"pmid":19244037,"doi":"10.1148/radiol.2503080253"},{"pmid":19332844,"doi":"10.1148/radiol.2511071897"},{"pmid":19401568,"doi":"10.1148/radiol.2512080485"},{"pmid":19401569,"doi":"10.1148/radiol.2512081235"},{"pmid":19474372,"doi":"10.1148/radiol.2513080636"},{"pmid":19561247,"doi":"10.1148/radiol.2513081280"},{"pmid":19703877,"doi":"10.1148/radiol.2522082335"},{"pmid":19717748,"doi":"10.1148/radiol.2523081972"},{"pmid":19717750,"doi":"10.1148/radiol.2523081929"},{"pmid":19789250,"doi":"10.1148/radiol.2531090611"},{"pmid":19789251,"doi":"10.1148/radiol.2531090689"},{"pmid":19789254,"doi":"10.1148/radiol.2531090302"},{"pmid":19864525,"doi":"10.1148/radiol.2532081199"},{"pmid":19864526,"doi":"10.1148/radiol.2532081738"},{"pmid":12511664,"doi":"10.1148/radiol.2261021292"},{"pmid":12511666,"doi":"10.1148/radiol.2261011296"},{"pmid":12563122,"doi":"10.1148/radiol.2262011600"},{"pmid":12563154,"doi":"10.1148/radiol.2262011992"},{"pmid":19952025,"doi":"10.1148/radiol.2533090179"},{"pmid":20032141,"doi":"10.1148/radiol.2541090361"},{"pmid":20032142,"doi":"10.1148/radiol.09090021"},{"pmid":20032157,"doi":"10.1148/radiol.09090690"},{"pmid":20089722,"doi":"10.1148/radiol.09090552"},{"pmid":20093507,"doi":"10.1148/radiol.2542082312"},{"pmid":20177082,"doi":"10.1148/radiol.09091264"},{"pmid":20177083,"doi":"10.1148/radiol.09092100"},{"pmid":20177084,"doi":"10.1148/radiol.09090330"},{"pmid":20177086,"doi":"10.1148/radiol.09091324"},{"pmid":20308442,"doi":"10.1148/radiol.09090339"},{"pmid":20413748,"doi":"10.1148/radiol.10090105"},{"pmid":20501711,"doi":"10.1148/radiol.10090877"},{"pmid":20505067,"doi":"10.1148/radiol.10100213"},{"pmid":20574084,"doi":"10.1148/radiol.10090908"},{"pmid":20574087,"doi":"10.1148/radiol.10091938"},{"pmid":20634431,"doi":"10.1148/radiol.10091982"},{"pmid":20720066,"doi":"10.1148/radiol.10092307"},{"pmid":20720065,"doi":"10.1148/radiol.10090397"},{"pmid":20736332,"doi":"10.1148/radiol.10100570"},{"pmid":20829537,"doi":"10.1148/radiol.10100070"},{"pmid":20851933,"doi":"10.1148/radiol.10091298"},{"pmid":20851934,"doi":"10.1148/radiol.10091480"},{"pmid":20851938,"doi":"10.1148/radiol.10091210"},{"pmid":20935079,"doi":"10.1148/radiol.10092373"},{"pmid":20959547,"doi":"10.1148/radiol.10091269"},{"pmid":21084413,"doi":"10.1148/radiol.10100140"},{"pmid":21084414,"doi":"10.1148/radiol.10081490"},{"pmid":21163918,"doi":"10.1148/radiol.10101157"},{"pmid":21183492,"doi":"10.1148/radiol.10092129"},{"pmid":21273517,"doi":"10.1148/radiol.10100161"},{"pmid":21273518,"doi":"10.1148/radiol.10100116"},{"pmid":21273519,"doi":"10.1148/radiol.10081634"},{"pmid":21330566,"doi":"10.1148/radiol.11100569"},{"pmid":21339346,"doi":"10.1148/radiol.10100376"},{"pmid":21339345,"doi":"10.1148/radiol.10100025"},{"pmid":21415247,"doi":"10.1148/radiol.11101887"},{"pmid":21436096,"doi":"10.1148/radiol.11100155"},{"pmid":21502390,"doi":"10.1148/radiol.11090563"},{"pmid":21502391,"doi":"10.1148/radiol.11091276"},{"pmid":21586679,"doi":"10.1148/radiol.11101352"},{"pmid":21602502,"doi":"10.1148/radiol.11081489"},{"pmid":21602503,"doi":"10.1148/radiol.11101362"},{"pmid":21693659,"doi":"10.1148/radiol.11110333"},{"pmid":21778451,"doi":"10.1148/radiol.11101359"},{"pmid":21778450,"doi":"10.1148/radiol.11101104"},{"pmid":21803921,"doi":"10.1148/radiol.11101344"},{"pmid":21931140,"doi":"10.1148/radiol.11101688"},{"pmid":21931139,"doi":"10.1148/radiol.11101922"},{"pmid":21931141,"doi":"10.1148/radiol.11091822"},{"pmid":22012900,"doi":"10.1148/radiol.11111099"},{"pmid":22012903,"doi":"10.1148/radiol.11091882"},{"pmid":22012902,"doi":"10.1148/radiol.11101426"},{"pmid":22012904,"doi":"10.1148/radiol.11091207"},{"pmid":22012899,"doi":"10.1148/radiol.11111131"},{"pmid":22095994,"doi":"10.1148/radiol.11110474"},{"pmid":22095995,"doi":"10.1148/radiol.11091710"},{"pmid":22156992,"doi":"10.1148/radiol.11110423"},{"pmid":22190655,"doi":"10.1148/radiol.11101996"},{"pmid":22190656,"doi":"10.1148/radiol.11110144"},{"pmid":22357880,"doi":"10.1148/radiol.11110947"},{"pmid":22357881,"doi":"10.1148/radiol.11101384"},{"pmid":22438443,"doi":"10.1148/radiol.11111111"},{"pmid":22438439,"doi":"10.1148/radiol.12110462"},{"pmid":22438440,"doi":"10.1148/radiol.11101821"},{"pmid":22517953,"doi":"10.1148/radiol.12110446"},{"pmid":22517956,"doi":"10.1148/radiol.12111869"},{"pmid":22517954,"doi":"10.1148/radiol.12110433"},{"pmid":22517959,"doi":"10.1148/radiol.12111605"},{"pmid":22623691,"doi":"10.1148/radiol.12110526"},{"pmid":22623690,"doi":"10.1148/radiol.12102394"},{"pmid":22623696,"doi":"10.1148/radiol.12112114"},{"pmid":22692035,"doi":"10.1148/radiol.12112265"},{"pmid":22723560,"doi":"10.1148/radiol.12110772"},{"pmid":22723559,"doi":"10.1148/radiol.12110339"},{"pmid":22798223,"doi":"10.1148/radiol.12111561"},{"pmid":22821690,"doi":"10.1148/radiol.12112678"},{"pmid":22821695,"doi":"10.1148/radiol.12111703"},{"pmid":22821694,"doi":"10.1148/radiol.12111658"},{"pmid":22919038,"doi":"10.1148/radiol.12110810"},{"pmid":22919039,"doi":"10.1148/radiol.12110357"},{"pmid":22993219,"doi":"10.1148/radiol.12111270"},{"pmid":22993217,"doi":"10.1148/radiol.12111769"},{"pmid":22966066,"doi":"10.1148/radiol.12112201"},{"pmid":23093707,"doi":"10.1148/radiol.12111740"},{"pmid":23175542,"doi":"10.1148/radiol.12120354"},{"pmid":23264525,"doi":"10.1148/radiol.12112469"},{"pmid":23220901,"doi":"10.1148/radiol.12110853"},{"pmid":23070271,"doi":"10.1148/radiol.12120240"}]
    for count, ident in enumerate(identifiers):
        doi = ident['doi']
        url = 'http://pubs.rsna.org/doi/full/%s' % doi
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
                    sys.stdout.write("limit reached, waiting...")
                    sleep(3600)
            entry_url = r.geturl()
            entry_html_source = r.read()
            soup = BeautifulSoup(entry_html_source.decode('utf-8'), 'html5lib')
            is_not_free = soup.find(id='accessDenialWidget')
            if is_not_free is not None:
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
                res_metadata[1] = 'Radiology'
                res_metadata[0] = doi
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
                    try:
                        f = urllib2.urlopen(urllib2.Request(figure[4]))
                        deadLinkFound = False
                    except:
                        deadLinkFound = True
                    if deadLinkFound:
                        url_correct = figure[3]
                    else:
                        url_correct = figure[4]
                    subres.append(Subresource(containing_resource = res,
                        name = figure[0],
                        type = 'figure',
                        content = figure[1],
                        url = url_correct))
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
            traceback.print_exc()'''
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    sys.stdout.write("~~~~loading concepts and term lists... ")
    start = time()
    file = open('scripts\MESH_concept_and_terms_tuple.pkl','rb')
    (tot_concepts, concept_IDs, term_lists) = pickle_zloads(file.read())
    file.close()
    sys.stdout.write("%.2f" % (time()-start) + "seconds\n")
    sys.stdout.flush()
    
    res_ids = list(Resource.objects.filter(type="Radiology").values_list('id',flat=True))
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
    
    bigA_AtA_sentence_path = 'matrices/Radiology_bigA_AtA_sentence.pkl'
    bigA_AtA_sentence_file = default_storage.open(bigA_AtA_sentence_path,'wb')
    mf = MatrixFiles(name='Radiology', type='AtA_sentence', path=bigA_AtA_sentence_path)
    mf.save()
    mf.user.add(9) # corresponds to admin@filopod.com
    bigA_AtA_sentence_tuple = (bigA_AtA_sentence, N_sentence)
    bigA_AtA_sentence_file.write(pickle_zdumps(bigA_AtA_sentence_tuple))
    bigA_AtA_sentence_file.close()
    
    #bigA_AtA_paragraph_path = 'matrices/Radiology_bigA_AtA_paragraph.pkl'
    #bigA_AtA_paragraph_file = default_storage.open(bigA_AtA_paragraph_path,'wb')
    #mf = MatrixFiles(name='Radiology', type='AtA_paragraph', path=bigA_AtA_paragraph_path)
    #mf.save()
    #mf.user.add(9) # corresponds to admin@filopod.com
    #bigA_AtA_paragraph_tuple = (bigA_AtA_paragraph, N_paragraph)
    #bigA_AtA_paragraph_file.write(pickle_zdumps(bigA_AtA_paragraph_tuple))
    #bigA_AtA_paragraph_file.close()
    
    sys.stdout.write("......" + str(time()-start) + " seconds\n")
    sys.stdout.flush()