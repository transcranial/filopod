# -*- coding: utf-8 -*- 
from filopod.support_functions import *
from main.models import *
import numpy
from django.core.files.storage import default_storage
from django.core.cache import cache

# Gets resource pack names
def get_respack_names():
    cache_key = 'respackNames'
    respack_names = cache.get(cache_key)
    if not respack_names:
        respack_names = sorted(set(MatrixFiles.objects.values_list('name',flat=True)))
        cache.set(cache_key, respack_names, 86400)
    return respack_names

# Gets list of resource pack names from code
def get_respack_names_from_code(respacks_code):
    cache_key = 'respackNamesFromCode_%s' % respacks_code
    respack_names_from_code = cache.get(cache_key)
    if not respack_names_from_code:
        respack_names_from_code = []
        respack_names = get_respack_names()
        for i, bit in enumerate(respacks_code):
            if bit == '1':
                respack_names_from_code.append(respack_names[i])
        cache.set(cache_key, respack_names_from_code, 86400)
    return respack_names_from_code

# Gets bigA associated with respack in list of respacks and sums all
def get_big_A(respacks_code, resolution):
    cache_key = 'bigA_%s_%s' % (respacks_code, resolution)
    x = get_chunked_from_cache(cache_key, 10)
    if x is not None:
        (big_A, N) = pickle_zloads(x)
    else: # using if not big_A raises error due to numpy.__nonzero__ system
        if resolution == 'sentence':
            mftype = 'AtA_sentence'
        elif resolution == 'paragraph':
            mftype = 'AtA_paragraph'
        else:
            raise Exception("'resolution' argument invalid.")
        respacks = get_respack_names_from_code(respacks_code)
        for i, respack in enumerate(respacks):
            matrix = MatrixFiles.objects.get(name=respack, type=mftype)
            tempdata = get_chunked_from_cache(matrix.path, 10)
            if not tempdata:
                file = default_storage.open(matrix.path,'rb')
                tempdata = file.read()
                file.close()
                set_chunked_to_cache(matrix.path, tempdata, 10)
            if i == 0:
                (big_A, N) = pickle_zloads(tempdata)
            else:
                (big_A_temp, N_temp) = pickle_zloads(tempdata)
                big_A = big_A + big_A_temp
                N = N + N_temp
        set_chunked_to_cache(cache_key, pickle_zdumps((big_A, N)), 10)
    return (big_A, N)

# Gets id of all concepts
def get_concept_IDs():
	cache_key = 'conceptIDs'
	concept_IDs = cache.get(cache_key)
	if not concept_IDs:
		concept_IDs = list(Concept.objects.values_list('id',flat=True))
		cache.set(cache_key, concept_IDs, 0)
	return concept_IDs
	
# Gets id of concepts with links
def get_conceptsWithLinks_IDs(respacks_code, resolution):
    cache_key = 'conceptsWithLinks_%s' % respacks_code
    conceptsWithLinks = cache.get(cache_key)
    if not conceptsWithLinks:
        (big_A, N) = get_big_A(respacks_code, resolution)
        if big_A is not None:
            nz_indices = big_A.diagonal().nonzero()[0].astype('int')
            idlist = nz_indices + 1
            conceptsWithLinks = idlist.tolist()
        else:
            conceptsWithLinks = []
        cache.set(cache_key, conceptsWithLinks, 0)
    return conceptsWithLinks

def get_concept_types():
    cache_key = 'conceptTypes'
    conceptTypes = cache.get(cache_key)
    if not conceptTypes:
        conceptTypeNames = list(set(Concept.objects.values_list('type',flat=True)))
        conceptTypeCodes = list(map(chr, range(97, 97+len(conceptTypeNames))))
        conceptTypes = []
        for i, name in enumerate(conceptTypeNames):
            conceptTypes.append({'name': name, 'code': conceptTypeCodes[i]})
        cache.set(cache_key, conceptTypes, 0)
    return conceptTypes
    
# Decodes concept type categories into strings
def get_concept_types_from_code(concept_type_code):
    cache_key = 'conceptTypesSelected_%s' % concept_type_code
    conceptTypesSelected = cache.get(cache_key)
    if not conceptTypesSelected:
        conceptTypesSelected = []
        conceptTypes = get_concept_types()
        for i in range(len(conceptTypes)):
            if conceptTypes[i]['code'] in concept_type_code:
                conceptTypesSelected.append(conceptTypes[i]['name'])
        cache.set(cache_key, conceptTypesSelected, 0)
    return conceptTypesSelected

# Gets id of all concepts, filtered by selected concept types
def get_concept_IDs_filteredByType(concept_type_code):
    cache_key = 'conceptIDs_filteredByType_%s' % concept_type_code
    concept_IDs_filteredByType = cache.get(cache_key)
    if not concept_IDs_filteredByType:
        conceptTypesSelected = get_concept_types_from_code(concept_type_code)
        concept_IDs_filteredByType = list(Concept.objects.filter(type__in=conceptTypesSelected).values_list('id',flat=True))
        cache.set(cache_key, concept_IDs_filteredByType, 0)
    return concept_IDs_filteredByType

# Gets id of all 'parent' concepts
def get_parentConcept_IDs(concept_id):
    cache_key = 'parentConcept_IDs_%s' % concept_id
    parentConcept_IDs = cache.get(cache_key)
    if not parentConcept_IDs:
        parentConcept_IDs = list(ConceptConceptLink.objects.filter(type='type of', source_concept_id=concept_id).values_list('target_concept_id',flat=True))
        cache.set(cache_key, parentConcept_IDs, 0)
    return parentConcept_IDs

#Gets list of terms for a concept
def get_termsList(concept_id):
    cache_key = 'termsList_%s' % str(concept_id)
    termsList = cache.get(cache_key)
    if not termsList:
        termsList = list(Term.objects.filter(concept_id=concept_id).values_list('name',flat=True))
        cache.set(cache_key, termsList, 0)
    return termsList

# Calculates association measures   
'''     n_ii counts (w1, w2), i.e. the bigram being scored
        n_ix counts (w1, *)
        n_xi counts (*, w2)
        n_xx counts (*, *), i.e. any bigram

    This may be shown with respect to a contingency table::

                w1    ~w1
             ------ ------
         w2 | n_ii | n_oi | = n_xi
             ------ ------
        ~w2 | n_io | n_oo |
             ------ ------
             = n_ix        TOTAL = n_xx
'''
# Pecina, Pavel. "Lexical association measures and collocation extraction." Language resources and evaluation 44.1-2 (2010): 137-158.
# Pecina, Pavel, and Pavel Schlesinger. "Combining association measures for collocation extraction." Proceedings of the COLING/ACL on Main conference poster sessions. Association for Computational Linguistics, 2006.
# Pecina, Pavel. "An extensive empirical study of collocation extraction methods." Proceedings of the ACL Student Research Workshop. Association for Computational Linguistics, 2005.
# Pecina, Pavel. "A machine learning approach to multiword expression extraction." Proceedings of the LREC MWE 2008 Workshop. 2008.
# Bouma, Gerlof. "Normalized (pointwise) mutual information in collocation extraction." Proceedings of the Biennial GSCL Conference. 2009.
def calcAssocMeasure(n_xy, n_x, n_y, N_total, measure_code):
    a = n_xy
    b = n_x - a
    c = n_y - a
    d = N_total - a - b - c
    if measure_code == 1: # conditional probability
        return n_xy / n_x
    elif measure_code == 2: # mutual dependence
        return numpy.log2(numpy.square(n_xy) / (n_x * n_y))
    elif measure_code == 3: # normalized expectation
        return 2 * a / (2 * a + b + c)
    elif measure_code == 4: # mutual expectation
        return (2 * a / (2 * a + b + c)) * (a / N_total)
    elif measure_code == 5: # Pearson phi coefficient
        return ((a * d) - (b * c)) / numpy.sqrt((a + b) * (a + c) * (b + d) * (c + d))
    elif measure_code == 6: # Student t test
        return (a - ((a + b) * (a + c) / N_total)) / numpy.sqrt(a * (1 - (a / N_total)))
    elif measure_code == 7: # z score
        return (a - ((a + b) * (a + c) / N_total)) / numpy.sqrt(((a + b) * (a + c) / N_total) * (1 - (((a + b) * (a + c) / N_total) / N_total)))
    elif measure_code == 8: # Russel-Rao
        return a / (a + b + c + d)
    elif measure_code == 9: # Jaccard
        return a / (a + b + c)
    elif measure_code == 10: # first Kulczynsky
        return a / (b + c)
    elif measure_code == 11: # second Sokal-Sneath
        return a / (a + 2 * (b + c))
    elif measure_code == 12: # Driver-Kroeber
        return n_xy / numpy.sqrt(n_x * n_y)
    elif measure_code == 13: # Fager
        return (n_xy / numpy.sqrt(n_x * n_y)) - (numpy.maximum(b, c) / 2)
    elif measure_code == 14: # Baroni-Urbani
        return (a + numpy.sqrt(a * d)) / (a + b + c + numpy.sqrt(a * d))
    elif measure_code == 15: # Michael
        return (4 * ((a * d) - (b * c))) / (numpy.square(a + d) + numpy.square(b + c))
    elif measure_code == 16: # Piatersky-Shapiro
        return (n_xy / N_total) - ((n_x / N_total) * (n_y / N_total))
    elif measure_code == 17: # Poisson-Stirling
        return n_xy * (numpy.log2(n_xy * N_total / (n_x * n_y)) - 1)
    else:
        return None    
        
#Gets subresources that contain both source_concept and target_concept
def get_filtSubres(respacks_code, source_concept_id, target_concept_id):
    cache_key = 'filtSubres_%s_%s_%s' % (respacks_code, str(source_concept_id), str(target_concept_id))
    filtSubres = cache.get(cache_key)
    if not filtSubres:
        respacks = get_respack_names_from_code(respacks_code)
        filtSubres = Subresource.objects.filter(containing_resource__type__in=respacks).filter(concepts_contained__id=source_concept_id).filter(concepts_contained__id=target_concept_id)
        cache.set(cache_key, filtSubres, 0)
    return filtSubres

# Given a rank-ordered list of concept nodes using association measures, further curate list based on various criteria        
def curate_concept_nodes(respacks_code, source_concept_id, target_concept_id_sortedList, numnodes):
    import math
    import re
    from nltk.tokenize import sent_tokenize
    n = 0
    source_terms = get_termsList(source_concept_id)
    source_terms_regex = [r"\b"+re.escape(term.lower())+r"\b" for term in source_terms]
    source_search_pattern = re.compile("|".join(source_terms_regex))
    final_concept_nodes = []
    final_concept_nodes_indicies = []
    final_concept_nodes_terms = []
    for i, target_concept_id in enumerate(target_concept_id_sortedList):
        target_terms = get_termsList(target_concept_id) 
        target_terms_regex = [r"\b"+re.escape(term.lower())+r"\b" for term in target_terms]
        target_terms_search_pattern = re.compile("|".join(target_terms_regex))
        # target concept must not be less specific version of source concept, e.g., infarction should not appear when myocardial infarction is source concept
        if len(target_terms_search_pattern.findall(". ".join([term.lower() for term in source_terms]))) == 0:
            # source concept and target concept must have paragraphs with more than one mention of either concept
            # if both appear only once in paragraph, more likely paragraph has other main topic, and the source and target concepts occur together only spuriously
            has_quality_subresources = False
            subresources = get_filtSubres(respacks_code, source_concept_id, target_concept_id)
            for subresource in subresources:
                paragraph = subresource.content
                source_terms_in_paragraph = len(source_search_pattern.findall(paragraph.lower()))
                target_terms_in_paragraph = len(target_terms_search_pattern.findall(paragraph.lower()))
                if subresource.type == 'figure': # boost scores for figures
                    source_terms_in_paragraph += 1
                    target_terms_in_paragraph += 1
                paragraph_score_geomean = math.sqrt(source_terms_in_paragraph * target_terms_in_paragraph)
                if paragraph_score_geomean > 1:
                    tokenized_sentences = sent_tokenize(paragraph)
                    for sentence in tokenized_sentences:
                        source_terms_in_sentence = len(source_search_pattern.findall(sentence.lower()))
                        target_terms_in_sentence = len(target_terms_search_pattern.findall(sentence.lower()))
                        sentence_score_geomean = math.sqrt(source_terms_in_sentence * target_terms_in_sentence)
                        if sentence_score_geomean >= 1:
                            has_quality_subresources = True
                            break
                    else:
                        continue
                    break
            if has_quality_subresources:
                if len(final_concept_nodes) == 0:
                        final_concept_nodes.append(target_concept_id)
                        final_concept_nodes_terms.append(target_terms)
                else:
                        has_subset = False
                        for j, final_concept_node_terms in enumerate(final_concept_nodes_terms):
                            # target concept must not have less specific version in the final list, e.g., infarction should not appear on same list as myocardial infarction  
                            if len(target_terms_search_pattern.findall(". ".join([term.lower() for term in final_concept_node_terms]))) > 0:
                                has_subset = True
                                break
                            else:
                                final_concept_node_terms_regex = [r"\b"+re.escape(term.lower())+r"\b" for term in final_concept_node_terms]
                                final_concept_node_terms_search_pattern = re.compile("|".join(final_concept_node_terms_regex))
                                if len(final_concept_node_terms_search_pattern.findall(". ".join([term.lower() for term in target_terms]))) > 0:
                                    final_concept_nodes.pop(j)
                                    final_concept_nodes_terms.pop(j)
                        if not has_subset:
                            final_concept_nodes.append(target_concept_id)
                            final_concept_nodes_indicies.append(i)
                            final_concept_nodes_terms.append(target_terms)
        if len(final_concept_nodes) == numnodes:
            break
    return final_concept_nodes, final_concept_nodes_indicies

# Gets JSON of subresource snippets, ranked by score
# Score is currently (paragraph_score_geomean / paragraph_length) * (sentence_score_geomean / sentence_length)
def getJSON_subresources_ranked(respacks_code, source_concept_id, target_concept_id):
    cache_key = 'subresources_JSON_%s_%s_%s' % (respacks_code, str(source_concept_id), str(target_concept_id))
    subresources_JSON = cache.get(cache_key)
    if not subresources_JSON:        
        import math
        import re
        from nltk.tokenize import sent_tokenize, word_tokenize
        source_terms = get_termsList(source_concept_id)
        target_terms = get_termsList(target_concept_id)
        source_terms_regex = [r"\b"+re.escape(term.lower())+r"\b" for term in source_terms]
        source_search_pattern = re.compile("|".join(source_terms_regex))
        target_terms_regex = [r"\b"+re.escape(term.lower())+r"\b" for term in target_terms]
        target_search_pattern = re.compile("|".join(target_terms_regex))
        sentence_scores = []
        subresource_json_list = []
        subresources = get_filtSubres(respacks_code, source_concept_id, target_concept_id)
        for subres_num, subresource in enumerate(subresources):
            paragraph = subresource.content
            source_terms_in_paragraph = len(source_search_pattern.findall(paragraph.lower()))
            target_terms_in_paragraph = len(target_search_pattern.findall(paragraph.lower()))
            if subresource.type == 'figure': # boost scores for figures
                source_terms_in_paragraph += 1
                target_terms_in_paragraph += 1
            paragraph_score_geomean = math.sqrt(source_terms_in_paragraph * target_terms_in_paragraph)
            # paragraph_score should be greater than 1 (each concept should not be mentioned just once)
            if paragraph_score_geomean > 1:
                paragraph_length = len(word_tokenize(paragraph))
                tokenized_sentences = sent_tokenize(paragraph)
                for sentence in tokenized_sentences:
                    sentence_length = len(word_tokenize(sentence))
                    source_terms_in_sentence = len(source_search_pattern.findall(sentence.lower()))
                    target_terms_in_sentence = len(target_search_pattern.findall(sentence.lower()))
                    sentence_score_geomean = math.sqrt(source_terms_in_sentence * target_terms_in_sentence)
                    if sentence_score_geomean >= 1:
                        sentence_scores.append((paragraph_score_geomean / paragraph_length) * (sentence_score_geomean / sentence_length))
                        if sentence[-1:] == ".":
                            snippet = sentence
                        else:
                            snippet = sentence + "."
                        subresource_json_list.append({
                            'resource_id': subresource.containing_resource_id,
                            'name': subresource.name,
                            'type': subresource.type,
                            'content': paragraph,
                            'snippet': snippet,
                            'url': subresource.url
                        })
        subresource_sorted_indices = sorted(range(len(sentence_scores)), key=lambda k: sentence_scores[k], reverse=True)
        subresources_JSON = [subresource_json_list[i] for i in subresource_sorted_indices]
        cache.set(cache_key, subresources_JSON, 0)
    return subresources_JSON