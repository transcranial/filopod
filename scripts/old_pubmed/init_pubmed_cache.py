from django.core.cache import cache
from main.views_exploration import get_chunked_from_cache, get_pubmed_Big_A, get_conceptsWithLinks_IDs_pubmed
from time import time
import sys
	
def run():
	start = time()
	print "initializing cache, pubmed bigA..."
	get_pubmed_Big_A('freq')
	print time()-start
	sys.stdout.flush()
	start = time()
	print "initializing cache, pubmed conceptsWithLinks_IDs..."
	get_conceptsWithLinks_IDs_pubmed()
	print time()-start
	sys.stdout.flush()
	
	start = time()
	cache_key = 'pubmed_bigA_freq'
	bigA = get_chunked_from_cache(cache_key, 100)
	if not bigA:
		print "pubmed_bigA not in cache"
	else:
		print "cached pubmed_bigA", time()-start
	sys.stdout.flush()
	
	start = time()
	cache_key = 'pubmed_conWithLinks'
	conceptsWithLinks = cache.get(cache_key)
	if not conceptsWithLinks:
		print "pubmed_conWithLinks not in cache"
	else:
		print "cached pubmed_conWithLinks", time()-start
	sys.stdout.flush()
