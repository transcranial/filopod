import cPickle as pickle
import zlib
import math
from django.core.cache import cache

#pickle and compress obj
def pickle_zdumps(obj):
    return zlib.compress(pickle.dumps(obj,pickle.HIGHEST_PROTOCOL),9)
	
#unpickle and decompress obj
def pickle_zloads(zstr):
    return pickle.loads(zlib.decompress(zstr)) 
	
#sets object in chunks to cache
def get_chunked_from_cache(cache_key, num_chunks):
    allChunksAvailable = all([(cache_key + '-%s' % i in cache) for i in range(num_chunks)])
    if allChunksAvailable:
        chunksCombined = ''.join([cache.get(cache_key + '-%s' % i) for i in range(num_chunks)])
        return chunksCombined
    else:
        return None  

#gets chunked object from cache
def set_chunked_to_cache(cache_key, obj, num_chunks):
    chunkSize = int(math.ceil(float(len(obj))/float(num_chunks)))
    obj_chunked = [obj[i:i+chunkSize] for i in range(0, len(obj), chunkSize)]
    for i, chunk in enumerate(obj_chunked):
        cache.set(cache_key + '-%s' % i, chunk, 0)
    return