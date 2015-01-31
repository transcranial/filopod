#be careful of bulk_create - bulk_size is not supported until Django 1.5 and mySQL has a limit of insertions which is >10,000, but still limited

from main.models import *
from bs4 import BeautifulSoup
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse
import httplib
import urlparse
from django.db.models import Q
from parserSelector import parserSelectorDict
from crunchRes import crunchRes
from time import time
from django.core.cache import cache

'''
Function: url_exists
Checks if a url path returns a 200 status response
'''
def url_exists(url):
	urlparts = urlparse.urlsplit(url)
	site = urlparts[1]
	path = urlparts[2]
	conn = httplib.HTTPConnection(site)
	conn.request('HEAD', path)
	response = conn.getresponse()
	conn.close()
	return response.status == 200

'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Gets domain ID from domain name
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
def get_domain_ID(domain_name):
	cache_key = 'domainID_' + domain_name
	domain_ID = cache.get(cache_key)
	if not domain_ID:
		domain_ID = Domain.objects.get(name=domain_name).id
		cache.set(cache_key, domain_ID, 0)
	return domain_ID
	
'''
Function: process_add_resources
Takes a POST request with an url and page source code, selects the appropriate parser, and calls the parser as a function to process the page source code. Resource and subresource (paragraphs and figures) objects are created based on the results of the parser.
'''
#function is csrf protected
@csrf_protect
def process_add_resource(request):
    if request.user.is_authenticated():
		domain_name = request.POST.get('domain_name', '')		
		# gets url and source from POST request
		html_url = request.POST.get('html_url', None)
		html_source = request.POST.get('html_source', None)	
				
		# makes sure html source is not empty
		if html_source is not None:		
			# uses beautiful soup to turn source into xml tree using the html5lib parser
			soup = BeautifulSoup(html_source, 'html5lib')
		
			#selects parser
			isHighwire = soup.find(class_='highwire-journal-article-marker-start')
			if isHighwire: # if journal is formatted using highwire
				parser = __import__('parser_HighWire', globals={"__name__": __name__})
			else:
				#selects correct parser based on domain of url
				for url_domain, parserFilename in parserSelectorDict.iteritems():
					if url_domain in html_url:
						parser = __import__(parserFilename, globals={"__name__": __name__})
						break
					else:
						parser = __import__('parser_generic', globals={"__name__": __name__})
			
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
			res_metadata = parser.get_metadata(html_url, soup)
			
			res_identifier = res_metadata[0]
			
			
			domain_ID = get_domain_ID(domain_name)
			# checks if Resource object already exists in database via identifier or url
			res_match = Resource.objects.filter(Q(identifier=res_identifier) | Q(url=html_url))
			if not res_match.count() == 0:
				# adds user making request to the matching Resource object
				if request.user.id not in res_match[0].user.values_list('id',flat=True):
					if domain_name in res_match[0].domain.values_list('name',flat=True):
						res_match[0].user.add(request.user.id)
					else:
						res_match[0].user.add(request.user.id)
						res_match[0].domain.add(domain_ID)
						# crunches the resource with new domain
						# queue crunchRes as celery task
						queued_task = crunchRes.delay(res_match[0].id,domain_ID,request.user.id)
						# add celery task to database, linked to requesting user
						QueuedResProcessTask(user=request.user, taskID=queued_task.id).save()
			else:
				# creates new Resource object and containing Subresource objects
				try:
					start = time()
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
						url = html_url,
						html_source = html_source)
					res.save()
					res.user.add(request.user.id) # adds user making request to newly created Resource object
					res.domain.add(domain_ID) # adds domain to newly created Resource object
					
					# creates Subresource objects of type 'figure'
					figures = parser.get_figures(html_url, soup)
					subres = []
					for i, figure in enumerate(figures):
						subres.append(Subresource(containing_resource = res,
							name = figure[0],
							type = 'figure',
							content = figure[1],
							url = figure[4]))
					
					# creates Subresource objects of type 'paragraph'
					paragraphs = parser.get_paragraphs(html_url, soup)
					
					for i, paragraph in enumerate(paragraphs):
						subres.append(Subresource(containing_resource = res,
							name = 'paragraph ' + str(i),
							type = 'paragraph',
							content = paragraph))
					subres_temp = Subresource.objects.bulk_create(subres)
					del subres_temp
					del subres
					print "time to write resource+subresources to db: " + str(time()-start) + " seconds"
							
					# crunches the resource
					# queue crunchRes as celery task
					queued_task = crunchRes.delay(res.id,domain_ID,request.user.id)
					# add celery task to database, linked to requesting user
					QueuedResProcessTask(user=request.user, taskID=queued_task.id).save()
				except Exception as inst:
					print inst
					return HttpResponse(status=500)
			return HttpResponse(status=200)
		else:	
			return HttpResponse(status=400)
    else:
		return HttpResponse(status=401)

