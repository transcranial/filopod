from time import time
import cPickle as pickle
import zlib
from main.models import *

'''pickle and compress obj'''
def pickle_zdumps(obj):
    return zlib.compress(pickle.dumps(obj,pickle.HIGHEST_PROTOCOL),9)

'''unpickle and decompress obj'''
def pickle_zloads(zstr):
    return pickle.loads(zlib.decompress(zstr))

def run():
    print "Loading concepts..."
    start = time()
    tot_concepts = Concept.objects.count()
    concept_IDs = list(Concept.objects.values_list('id',flat=True))
    print "%.2f" % (time()-start) + " seconds"
    term_lists = []
    print "Loading terms..."
    for con_id in concept_IDs:
        if con_id % 100 == 1:
            start = time()
        term_lists.append(list(Term.objects.filter(concept_id=con_id).values_list('name',flat=True)))
        if con_id % 100 == 0:
            print "concept #: " + str(con_id) + " - %.2f" % ((tot_concepts-con_id) * (time()-start) / 100) + " seconds to go"
    print "Saving file..."
    start = time()
    file = open('scripts\MESH_concept_and_terms_tuple.pkl','wb')
    file.write(pickle_zdumps((tot_concepts, concept_IDs, term_lists)))
    file.close()
    print "%.2f" % (time()-start) + " seconds"