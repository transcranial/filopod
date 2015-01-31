#this method is designed to clean up the poop produced by the crunchRes script in case it fails
#it is designed to clean up the poop no matter what stage the script fails
#it also deletes the resource, which deletes all the subresources associated
#and therefore can be used to delete resources from a user's library
#NOTE that if that resource is still useful for another user, it will not be deleted

#These are the specific poop to be removed:
#(0)User from the resource
#(1)Resources if no longer needed
#(2)Subresources if no longer needed
#(3)raw count matrix
#(4)AtA matrix
#(5)covA matrix

from main.models import *
from time import time
import celery
from celery.result import AsyncResult as celery_result
from django.core.files.storage import default_storage
from django.core.cache import cache

'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Gets cache generation number for user. 
Generation number if used for versioning cached contents. 
It is incremented every time the user's underlying data, e.g. big_A, changes, such as when a resource is added or deleted.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''		
def get_user_generation(user_ID):
	cache_key = 'gen' + str(user_ID)
	generation = cache.get(cache_key)
	if not generation:
		generation = 1
		cache.set(cache_key, generation, 0)
	return generation
	
'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
cleanRes function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''	
@celery.task
def cleanupRes(resource_ID,domain_ID,user_ID):
	if celery_result(celery.current_task.request.id).state == 'SUCCESS':
		return
	else:
		try:
			print "***starting cleanupRes: resourceID %s, domainID %s, userID %s***" % (resource_ID,domain_ID,user_ID)
			res = Resource.objects.get(id=resource_ID)
			
			#first delete user from resource
			try:
				res.user.remove(user_ID)
				print "    user removed from resource."
			except Exception:
				pass
			
			#if no other users, then delete resource created, all subresources are also removed
			if res.user.count() == 0:
				print "    resource has no other users, deleting resource and files..."
				matrices = MatrixFileSystem.objects.filter(resource_id=resource_ID, domain_id=domain_ID)
				for matrix in matrices:
					print "    %s matrix file deleted from S3." % matrix.type
					default_storage.delete(matrix.path)			
				res.delete() # will also delete associated MatrixFileSystem objects
				print "    resource deleted from database."
			
			get_user_generation(user_ID)
			cache.incr('gen' + str(user_ID))
			print "    cache generation number for user incremented."
			success = True
		except Exception as inst:
			print inst
			success = False
		
		try:
			QueuedResProcessTask.objects.get(taskID=celery.current_task.request.id).delete()
		except Exception:
			pass
		
		return success