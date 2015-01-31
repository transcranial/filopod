  
import pickle
import zlib

'''pickle and compress obj'''
def pickle_zdumps(obj):
    return zlib.compress(pickle.dumps(obj,pickle.HIGHEST_PROTOCOL),9)

'''unpickle and decompress obj'''
def pickle_zloads(zstr):
    return pickle.loads(zlib.decompress(zstr))
    
    
file = open('MESH_concept_and_terms_tuple.pkl','rb')
(tot_concepts, concept_IDs, term_lists) = pickle_zloads(file.read())
file.close()

file = open('MESH_termlists.pkl','wb')
file.write(pickle_zdumps(term_lists))
file.close()