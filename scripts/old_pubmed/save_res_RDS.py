from main.models import *
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
	
'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
to be run on EC2
saves resource and subresources in RDS
Filopod admin account: ID=9
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''		
def run():
	filenumber_start = 747
	filenumber_stop = 797
	#tot abstracts from 747 to 797: 691742
	i = filenumber_start
	tot_abstracts = 0
	looptime = 0
	while i <= filenumber_stop:
		print "reading file: %s" % str(i)
		sys.stdout.flush()
		path = "scripts/files_for_ec2/res_abstract_containedcon_tuplelist_medline13n0%s.pkl" % str(i)
		file = open(path,'rb')
		temp_tuplelist = pickle_zloads(file.read())
		file.close()
		tot_abstracts = tot_abstracts + len(temp_tuplelist)
		i = i+1
		j = 0
		sys.stdout.write("saving Resource/Subresource objects in database... ")
		sys.stdout.flush()
		for (res, abstract, concept_IDs_contained) in temp_tuplelist:
			start = time()
			if j % 1000 == 0:
				sys.stdout.write("    " + str(int(j*100/len(temp_tuplelist))) + "% " + "[time remaining: " + str(int(looptime * (len(temp_tuplelist)-j))) + "]\n")
				sys.stdout.flush()
			res.save()
			res.user.add(9)
			res.domain.add(1)
			subres = Subresource.objects.create(containing_resource = res,
				type = 'abstract',
				content = abstract)
			subres.concepts_contained.add(*concept_IDs_contained)
			j = j+1
			looptime = time()-start
	print "#### Total number of abstracts: %s" % str(tot_abstracts)
	sys.stdout.flush()
	