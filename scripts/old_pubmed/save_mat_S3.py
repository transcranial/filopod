from django.core.files.storage import default_storage
from time import time
import traceback
import sys
import cPickle as pickle
import zlib

'''pickle and compress obj'''
def pickle_zdumps(obj):
	return zlib.compress(pickle.dumps(obj,pickle.HIGHEST_PROTOCOL),9)

'''unpickle and decompress obj'''
def pickle_zloads(zstr):
	return pickle.loads(zlib.decompress(zstr))

def run():
	filenumber_start = 747
	filenumber_stop = 797
	
	path = "scripts/pubmed_matrices/pubmed_0%s_0%s_rawA.pkl" % (str(filenumber_start), str(filenumber_stop))
	file = open(path,'rb')
	rawA = pickle_zloads(file.read())
	file.close()
	path = "matrices/pubmed/pubmed_0%s_0%s_rawA.pkl" % (str(filenumber_start), str(filenumber_stop))
	file = default_storage.open(path,'wb')
	file.write(pickle_zdumps(rawA))
	file.close()
	
	path = "scripts/pubmed_matrices/pubmed_0%s_0%s_bigA.pkl" % (str(filenumber_start), str(filenumber_stop))
	file = open(path,'rb')
	bigA = pickle_zloads(file.read())
	file.close()
	path = "matrices/pubmed/pubmed_0%s_0%s_bigA.pkl" % (str(filenumber_start), str(filenumber_stop))
	file = default_storage.open(path,'wb')
	file.write(pickle_zdumps(bigA))
	file.close()