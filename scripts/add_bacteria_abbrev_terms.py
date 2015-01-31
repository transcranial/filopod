'''
Bacteria concepts in MESH do not contain terms for the common abbreviated spelling:
concept for Staphylococcus aureus does not contain "S. aureus" as a term.

This script adds all these terms using regex.
'''
from main.models import *

def run():
    bacteriaConcepts = Concept.objects.filter(conceptID__startswith='B03').filter(name__regex=r'^[[:alpha:]]+[[:space:]][a-z]+$')
    bacteriaAbbrevTermList = []
    for i, bacteria in enumerate(bacteriaConcepts):
        splitTerm = (bacteria.name).split(' ')
        abbrev = splitTerm[0][0] + '. ' + splitTerm[1]        
        bacteriaAbbrevTerm = Term(name=abbrev, concept=bacteria)
        bacteriaAbbrevTermList.append(bacteriaAbbrevTerm)
        print i
    Term.objects.bulk_create(bacteriaAbbrevTermList)
    print 'Successfully added ' + str(len(bacteriaAbbrevTermList)) + ' abbreviated bacteria terms.'