from scipy.sparse import coo_matrix, csr_matrix, vstack
from scipy import int16
from numpy import array
import math
import sys
import cPickle as pickle
import zlib
from time import time

'''pickle and compress obj'''
def pickle_zdumps(obj):
	return zlib.compress(pickle.dumps(obj,pickle.HIGHEST_PROTOCOL),9)

'''unpickle and decompress obj'''
def pickle_zloads(zstr):
	return pickle.loads(zlib.decompress(zstr))
	
def run():
	filenumber_start = 747
	filenumber_stop = 797
	i = filenumber_start
	while i <= filenumber_stop:
		sys.stdout.write(str(i) + " ")
		path = "scripts\\pubmed_matrices\\rawA_medline13n0%s.pkl" % str(i)
		file = open(path,'rb')
		temp_rawA = pickle_zloads(file.read())
		if i == filenumber_start:
			target_A = temp_rawA
		else:
			target_A = vstack([target_A, temp_rawA])
		file.close()
		i = i+1
	
	sys.stdout.write("creating and saving rawA matrix... ")
	start = time()
	path = "scripts\\pubmed_matrices\\pubmed_0%s_0%s_rawA.pkl" % (str(filenumber_start), str(filenumber_stop))
	file = open(path,'wb')
	file.write(pickle_zdumps(target_A))
	file.close()
	print "%.2f" % (time()-start), "seconds"
	
	sys.stdout.write("creating and saving bigA matrix... ")
	start = time()
	AtA = target_A.T * target_A
	path = "scripts\\pubmed_matrices\\pubmed_0%s_0%s_bigA.pkl" % (str(filenumber_start), str(filenumber_stop))
	file = open(path,'wb')
	file.write(pickle_zdumps(AtA))
	file.close()
	print "%.2f" % (time()-start), "seconds"
	
	# memory requirements are not sufficient for this currently
	'''sys.stdout.write("creating and saving covA matrix... ")
	start = time()
	raw_A = target_A.astype(float)
	mean_vector = csr_matrix(raw_A.mean(axis=0))
	norm_A = raw_A - csr_matrix([1]*raw_A.shape[0]).T * mean_vector
	norm_A = norm_A.tocsr()
	covariance_matrix = (norm_A.T * norm_A) / raw_A.shape[0]	
	path = "scripts\\pubmed_matrices\\pubmed_0%s_0%s_covA.pkl" % (str(filenumber_start), str(filenumber_stop))
	file = open(path,'wb')
	file.write(pickle_zdumps(covariance_matrix))
	file.close()
	print "%.2f" % (time()-start), "seconds"'''