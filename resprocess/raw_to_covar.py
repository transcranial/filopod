from main.models import *
import pickle
from scipy.sparse import csr_matrix
from time import time
import uuid
from django.core.files.storage import default_storage

def run():
    resource_ID = raw_input("r = ")
    domain_ID = raw_input("d = ")
    print "***compiling covariance matrix***"
    start = time()
    r = Resource.objects.get(id=resource_ID) #get resource
    d = Domain.objects.get(id=domain_ID) #get domain
    try:
        mfs_raw_path = MatrixFileSystem.objects.get(resource=r,domain=d,type="rawA").path #get path from MFS
        #get the file
        file = default_storage.open(mfs_raw_path) 
        raw_A = pickle.load(file)
        file.close()
    except Exception:
        print " sorry, file could not be found."
        return False

    #calculate covariance matrix
    raw_A = raw_A.astype(float)
    mean_vector = csr_matrix(raw_A.mean(axis=0))
    norm_A = raw_A - csr_matrix([1]*raw_A.shape[0]).T * mean_vector
    norm_A = norm_A.tocsr()
    covariance_matrix = (norm_A.T * norm_A) / raw_A.shape[0]

    #save the file
    uid_name = uuid.uuid4().hex
    path = 'matrices/covA/' + uid_name + '.pkl'
    mfs_cov_path = MatrixFileSystem(resource=r,domain=d,type="covA",path=path)
    file = default_storage.open(path,'wb')
    pickle.dump(covariance_matrix,file)
    file.close()
    mfs_cov_path.save()
    
    print " finished constructing covariance matrix..." + str(time()-start) + " seconds"
    
    return True
