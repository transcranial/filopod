from filopod.support_functions import *
from main.models import MatrixFiles
from django.core.files.storage import default_storage
from django.core.cache import cache

def run():
    for MF in MatrixFiles.objects.all():
        path = MF.path
        bigA_file = default_storage.open(path,'rb')
        cache_key = path
        set_chunked_to_cache(cache_key, bigA_file.read(), 10)
    
    try:
        cache.delete('respackNames')
        temp = get_respack_names()
    except:
        pass
    
    try:
        cache.delete('conceptIDs')
        temp = get_concept_IDs()
    except:
        pass
    
    try:
        cache.delete('conceptTypes')
        temp = get_concept_types()
    except:
        pass
    
    concept_type_code = 'abcdeg'
    
    try:
        cache.delete('conceptTypesSelected_%s' % concept_type_code)
        temp = get_concept_types_from_code(concept_type_code)
    except:
        pass  
        
    try:
        cache.delete('conceptIDs_filteredByType_%s' % concept_type_code)
        temp = get_concept_IDs_filteredByType(concept_type_code)
    except:
        pass
    
    respacks_codes = ['0011000', '1100000', '0000100', '0000011', '0011011']
    
    for respacks_code in respacks_codes:
        try:
            cache.delete('respackNamesFromCode_%s' % respacks_code)
            temp = get_respack_names_from_code(respacks_code)
        except:
            pass
        
        try:
            cache.delete('bigA_%s_%s' % (respacks_code, 'sentence'))
            temp = get_big_A(respacks_code, 'sentence')
        except:
            pass
        
        try:
            cache.delete('conceptsWithLinks_%s' % respacks_code)
            temp = get_conceptsWithLinks_IDs(respacks_code, 'sentence')
        except:
            pass