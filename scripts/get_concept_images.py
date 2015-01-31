#! download image from first Bing image search result of concept names

import urllib
import mechanize
import cookielib
from bs4 import BeautifulSoup
from time import time
from time import sleep
import re
from main.models import Concept

def run():
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
    # User-Agent (this is cheating, ok?)
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
    print "initiated browser: " + str(time()-start) + " seconds"
    
    start = time()
    concept_names = list(Concept.objects.values_list('name',flat=True))
    concept_ids = list(Concept.objects.values_list('id',flat=True))
    print "obtained concepts: " + str(time()-start) + " seconds"
    for i in range(0, len(concept_names)):
        if i % 200 == 0:
            start = time()
            br = mechanize.Browser()
            cj = cookielib.LWPCookieJar()
            br.set_cookiejar(cj)
            br.set_handle_equiv(True)
            br.set_handle_redirect(True)
            br.set_handle_referer(True)
            br.set_handle_robots(False)
            br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
            br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
            print "initiated browser: " + str(time()-start) + " seconds"
        start = time()
        html_url = 'http://www.bing.com/images/search?q=' + urllib.quote_plus(concept_names[i])
        r = br.open(html_url)
        html_source = r.read()
        soup = BeautifulSoup(html_source, 'lxml')
        image_div = soup.find(class_='dg_u')
        if image_div is not None:
            image = image_div.find('img')
            if image is not None:
                urllib.urlretrieve(image['src2'], "filopod/static/images/concepts/" + str(concept_ids[i]) + ".jpg")
        print "concept #" + str(i+1) + ": " + str(time()-start) + " seconds"