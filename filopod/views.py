# -*- coding: utf-8 -*- 
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.core.cache import cache
import traceback
import simplejson as json
from main.models import *
from filopod.main_functions import *
	
def about(request):
    page = request.GET.get('p','')
    if page == 'respacks':
        cache_key = 'respackInfo'
        respack_info = cache.get(cache_key)
        if not respack_info:
            respack_names = get_respack_names()
            respack_info = []
            for respack in respack_names:
                resNum = Resource.objects.filter(type=respack).count()
                resOldest = Resource.objects.filter(type=respack).order_by('date')[0].date.replace('/','-')
                resNewest = Resource.objects.filter(type=respack).order_by('-date')[0].date.replace('/','-')
                subresNum = Subresource.objects.filter(containing_resource__type=respack).count()
                if respack == 'NEJM review articles':
                    resInfo = "Compiled from recent New England Journal of Medicine review articles. The quality of these resources are top notch."
                    logofile = "sites_nejm.png"
                elif respack == 'JAMA review articles':
                    resInfo = "Compiled from select Journal of the American Medical Association review articles over the last decade."
                    logofile = "sites_jama.png"
                elif respack == 'Pediatrics':
                    resInfo = "Compiled from recent select Pediatrics review articles with full-text available free online."
                    logofile = "sites_pediatrics.png"
                elif respack == 'Radiology':
                    resInfo = "Compiled from select Radiology review articles over the last 10 years."
                    logofile = "sites_radiology.png"
                elif respack == 'RadioGraphics':
                    resInfo = "Compiled from RadioGraphics review articles over the last 10 years."
                    logofile = "sites_radiographics.png"
                elif respack == 'J of Neuroscience':
                    resInfo = "Compiled from select Journal of Neuroscience review articles over the last 10 years."
                    logofile = "sites_jneurosci.png"
                elif respack == 'Brain':
                    resInfo = "Compiled from select Brain review articles over the last 10 years."
                    logofile = "sites_brain.png"
                else:
                    resInfo = ""
                info = {
                    'name': respack,
                    'resNum': resNum,
                    'subresNum': subresNum,
                    'resOldest': resOldest,
                    'resNewest': resNewest,
                    'resInfo': resInfo,
                    'logofile': logofile
                }
                respack_info.append(info)
            cache.set(cache_key, respack_info, 86400)
        template_dict = {
            'respacksList': respack_info
        }
    else:
        template_dict = {}
    return render_to_response('about/' + page + '.html', template_dict, RequestContext(request))
	
def tos(request):
    return render_to_response('doc/tos.html', RequestContext(request))
	
def privacy(request):
    return render_to_response('doc/privacy.html', RequestContext(request))
	
def publishers(request):
    return render_to_response('doc/publishers.html', RequestContext(request))

def home(request):
    respack_names = get_respack_names()
    conceptTypes = get_concept_types()
    template_dict = {
        'respacks': {
            'names': respack_names,
            'default': ''.join(['1' if (
                respack=='NEJM review articles' or 
                respack=='JAMA review articles') else '0' for respack in respack_names])
        },
        'number_nodes': {
            'n': [5, 10, 15, 20, 25, 30, 35, 40, 45, 50],
            'default': 25
        },
        'concept_types': {
            'types': conceptTypes,
            'default': 'abcdeg'
        },
        'assoc_measures': {
            'measures': [{'name': 'conditional probability', 'code': '1'},
                {'name': 'mutual dependence', 'code': '2'},
                {'name': 'normalized expectation', 'code': '3'},
                {'name': 'mutual expectation', 'code': '4'},
                {'name': 'Pearson phi coefficient', 'code': '5'},
                {'name': 'Student t test', 'code': '6'},
                {'name': 'Z score', 'code': '7'},
                {'name': 'Russel-Rao', 'code': '8'},
                {'name': 'Jaccard', 'code': '9'},
                {'name': 'first Kulczynsky', 'code': '10'},
                {'name': 'second Sokal-Sneath', 'code': '11'},
                {'name': 'Driver-Kroeber', 'code': '12'},
                {'name': 'Fager', 'code': '13'},
                {'name': 'Baroni-Urbani', 'code': '14'},
                {'name': 'Michael', 'code': '15'},
                {'name': 'Piatersky-Shapiro', 'code': '16'},
                {'name': 'Poisson-Stirling', 'code': '17'},
                {'name': 'combine all', 'code': '0'}],
            'default': {'name': 'combine all', 'code': '0'}
        }
    }
    return render_to_response('index.html', template_dict, RequestContext(request))

def get_search_concepts(request):
    if request.is_ajax():
        try:
            q = request.GET.get('query', '')
            respacks_code = request.GET.get('respacks_code', '')
            cache_key = 'getSearchConcepts_%s_%s' % (q.replace(' ','%20'), respacks_code)
            data = cache.get(cache_key)
            if not data:
                conceptsWithLinks = get_conceptsWithLinks_IDs(respacks_code, 'sentence')
                terms = Term.objects.filter(name__icontains = q).select_related('concept__name')
                concept_ids = []
                concepts = []
                terms_in_concepts = []
                for term in terms:
                    if len(concepts) == 20:
                        break
                    if term.concept_id in conceptsWithLinks and term.concept_id not in concept_ids:
                        concept_ids.append(term.concept_id)
                        concepts.append(term.concept.name)
                        terms_in_concepts.append(get_termsList(term.concept_id))
                data = json.dumps({'concept_ids': concept_ids, 'concepts': concepts, 'terms': terms_in_concepts})
                cache.set(cache_key, data, 0)
        except Exception as inst:
            print inst
            traceback.print_exc()
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)
    
def get_concept_nodes(request):
    if request.is_ajax():
        try:
            concept_id = int(request.GET.get('concept_id', ''))
            respacks_code = request.GET.get('respacks_code', '')
            numnodes = int(request.GET.get('numnodes', ''))
            concept_types_code = request.GET.get('concept_types_code', '')
            assoc_measure = int(request.GET.get('assoc_measure', ''))
            cache_key = 'getConceptNodes_%s_%s_%s_%s_%s' % (str(concept_id), respacks_code, str(numnodes), concept_types_code, str(assoc_measure))
            data = cache.get(cache_key)
            if not data:
                import numpy
                (big_A, N_total) = get_big_A(respacks_code, 'sentence')
                nz_indices = big_A[concept_id - 1, :].nonzero()[1]                
                parentConcept_IDs = get_parentConcept_IDs(concept_id)
                concept_IDs_manuallyExclude = [4239, 3773, 19852, 23511, 8276, 4616, 8498, 20051, 3969, 22079]
                # exclude source concept
                nz_indices_filtered = numpy.setdiff1d(nz_indices, numpy.array([concept_id]) - 1)
                # exclude parent concepts
                nz_indices_filtered = numpy.setdiff1d(nz_indices_filtered, numpy.array(parentConcept_IDs) - 1)
                # exclude manual exclusions
                nz_indices_filtered = numpy.setdiff1d(nz_indices_filtered, numpy.array(concept_IDs_manuallyExclude) - 1)
                # exclude concept types not selected
                concept_IDs_filteredByType = get_concept_IDs_filteredByType(concept_types_code)
                nz_indices_filtered = numpy.intersect1d(nz_indices_filtered, numpy.array(concept_IDs_filteredByType) - 1)
                concept_nodes_ID_filtered = nz_indices_filtered + 1                
                n_xy = big_A[concept_id - 1, nz_indices_filtered].astype('float').toarray()[0]
                n_x = big_A[concept_id - 1, concept_id - 1].astype('float')
                n_y = big_A.diagonal()[nz_indices_filtered].astype('float')                
                if assoc_measure in range(0,18):
                    if assoc_measure == 0:
                        rankingLists = []
                        for m in range(1,18):
                            associationMeasureArray = calcAssocMeasure(n_xy, n_x, n_y, N_total, m)
                            ranking = (- associationMeasureArray).argsort().argsort()
                            rankingLists.append(ranking)
                        avg_ranking = numpy.mean(numpy.vstack(tuple(rankingLists)), axis=0)
                        j_sorted = avg_ranking.argsort()
                        nodesID, final_indices = curate_concept_nodes(respacks_code, concept_id, concept_nodes_ID_filtered[j_sorted].tolist(), numnodes)
                        j_top = j_sorted[numpy.array(final_indices)]
                        max_ranking_top = numpy.amax(avg_ranking[j_top], axis=0)
                        avg_ranking_top = avg_ranking[j_top]
                        nodesValue = numpy.ceil(100 * (max_ranking_top - avg_ranking_top) / max_ranking_top).astype('int8').tolist()
                    else:
                        associationMeasureArray = calcAssocMeasure(n_xy, n_x, n_y, N_total, assoc_measure)
                        j_sorted = (- associationMeasureArray).argsort()
                        nodesID, final_indices = curate_concept_nodes(respacks_code, concept_id, concept_nodes_ID_filtered[j_sorted].tolist(), numnodes)
                        j_top = j_sorted[numpy.array(final_indices)]
                        associationMeasureArray_max = numpy.amax(associationMeasureArray[j_top], axis=0)
                        nodesValue = numpy.ceil(100 * associationMeasureArray[j_top] / associationMeasureArray_max).astype('int8').tolist()
                    concepts = dict(Concept.objects.filter(id__in=nodesID).values_list('id','name'))
                    nodesName = [concepts[id] for id in nodesID]
                    nodesTerms = [get_termsList(id) for id in nodesID]
                else:
                    raise Exception("'association measure' code is invalid.")
                data = json.dumps({'nodesIndex': nodesID, 'nodesName': nodesName, 'nodesTerms': nodesTerms, 'nodesValue': nodesValue})
                cache.set(cache_key, data, 0)
        except Exception as inst:
            print inst
            traceback.print_exc()
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)
    
def fetch_resources(request):
    if request.is_ajax():
        try:
            respacks_code = request.GET.get('respacks_code', '')
            source_concept_id = int(request.GET.get('source_concept_id', ''))
            target_concept_id = int(request.GET.get('target_concept_id', ''))
            page = int(request.GET.get('page'))
            cache_key = 'fetchedResources_%s_%s_%s_%s' % (respacks_code, str(source_concept_id), str(target_concept_id), str(page))
            data = cache.get(cache_key)
            if not data:
                from django.core.paginator import Paginator
                max_snippets_per_page = 10 # max items for paginator
                subresources_JSON = getJSON_subresources_ranked(respacks_code, source_concept_id, target_concept_id)
                subresources_JSON_paginator = Paginator(subresources_JSON, max_snippets_per_page)
                subresources_JSON_page = subresources_JSON_paginator.page(page)
                subresources_JSON_page_objects = subresources_JSON_page.object_list
                resources_JSON = []
                subset_resource_id_list = [element['resource_id'] for element in subresources_JSON_page_objects]
                resources = Resource.objects.in_bulk(subset_resource_id_list)		
                for id in subset_resource_id_list:
                    res = resources[id]
                    resources_JSON.append({
                        'id': res.id,
                        'identifier': res.identifier,
                        'type': res.type, 
                        'title': res.title.replace('"','&quot;').replace("'",'&#39;'),
                        'author': res.author.replace('"','&quot;').replace("'",'&#39;'),
                        'journal': res.journal,
                        'volume': res.volume,
                        'issue': res.issue,
                        'firstpage': res.firstpage,
                        'lastpage': res.lastpage,
                        'date': res.date,
                        'publisher': res.publisher,
                        'url': res.url
                    })
                data = json.dumps({
                    'subresources_totnum': len(subresources_JSON),
                    'resources_paginated': resources_JSON,
                    'subresources_paginated': subresources_JSON_page_objects,
                    'current_page': subresources_JSON_page.number, 
                    'num_pages': subresources_JSON_paginator.num_pages, 
                    'has_previous': subresources_JSON_page.has_previous(), 
                    'has_next': subresources_JSON_page.has_next()
                }, ensure_ascii=False, use_decimal=True)
                cache.set(cache_key, data, 0)
        except Exception as inst:
            print inst
            traceback.print_exc()
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)