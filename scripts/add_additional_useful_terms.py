'''
Some MESH concepts don't contain all useful containing terms.
For example, 'Magnetic Resonance Imaging' does not contain 'MRI' or 'MRI image', but has 'MRI scan'

This script adds additional terms.
'''
from main.models import *
from filopod.main_functions import get_termsList

def run():
    newTermList = []
    
    con = Concept.objects.get(name__iexact="magnetic resonance imaging")
    terms = get_termsList(con.id)
    proposed_terms = ["MRI", "MRI image", "MRI images", "MR image", "MR images", "MRI imaging", "MR imaging", "MR spectroscopy", "fMRI", "function MRI"]
    for proposed_term in proposed_terms:
        if proposed_term not in terms:
            newTermList.append(Term(name=proposed_term, concept=con))
    
    con = Concept.objects.get(name__iexact="diffusion magnetic resonance imaging")
    terms = get_termsList(con.id)
    proposed_terms = ["diffusion MR", "dMRI", "d-MRI", "diffusion-MR", "diffusion-MRI", "diffusion-weighted MR", "diffusion-weighted MRI"]
    for proposed_term in proposed_terms:
        if proposed_term not in terms:
            newTermList.append(Term(name=proposed_term, concept=con))
    
    con = Concept.objects.get(name__iexact="Diffusion Tensor Imaging")
    terms = get_termsList(con.id)
    proposed_terms = ["diffusion tensor MR imaging", "diffusion tensor MR image", "diffusion tensor MR images", "diffusion tensor MRI"]
    for proposed_term in proposed_terms:
        if proposed_term not in terms:
            newTermList.append(Term(name=proposed_term, concept=con))
    
    con = Concept.objects.get(name__iexact="magnetic resonance angiography")
    terms = get_termsList(con.id)
    proposed_terms = ["MRA", "MRV", "MR angiography", "MR aortography", "MR venography", "MRI angiography", "MRI aortography", "MRI venography"]
    for proposed_term in proposed_terms:
        if proposed_term not in terms:
            newTermList.append(Term(name=proposed_term, concept=con))
    
    con = Concept.objects.get(name__iexact="magnetic resonance imaging, cine")
    terms = get_termsList(con.id)
    proposed_terms = ["cine MR image", "cine MR images", "cine MR imaging"]
    for proposed_term in proposed_terms:
        if proposed_term not in terms:
            newTermList.append(Term(name=proposed_term, concept=con))
    
    con = Concept.objects.get(name__iexact="magnetic resonance imaging, interventional")
    terms = get_termsList(con.id)
    proposed_terms = ["interventional MR image", "interventional MR images", "interventional MR imaging", "interventional MR angiography"]
    for proposed_term in proposed_terms:
        if proposed_term not in terms:
            newTermList.append(Term(name=proposed_term, concept=con))
    
    con = Concept.objects.get(name__iexact="Echocardiography")
    terms = get_termsList(con.id)
    proposed_terms = ["echocardiogram"]
    for proposed_term in proposed_terms:
        if proposed_term not in terms:
            newTermList.append(Term(name=proposed_term, concept=con))
    
    con = Concept.objects.get(name__iexact="Echocardiography, Doppler")
    terms = get_termsList(con.id)
    proposed_terms = ["Doppler echocardiogram", "Doppler echo"]
    for proposed_term in proposed_terms:
        if proposed_term not in terms:
            newTermList.append(Term(name=proposed_term, concept=con))
    
    con = Concept.objects.get(name__iexact="Echocardiography, Stress")
    terms = get_termsList(con.id)
    proposed_terms = ["stress echo", "stress echocardiogram"]
    for proposed_term in proposed_terms:
        if proposed_term not in terms:
            newTermList.append(Term(name=proposed_term, concept=con))
    
    con = Concept.objects.get(name__iexact="Echocardiography, Three-Dimensional")
    terms = get_termsList(con.id)
    proposed_terms = ["3D echocardiogram", "3-D echocardiogram"]
    for proposed_term in proposed_terms:
        if proposed_term not in terms:
            newTermList.append(Term(name=proposed_term, concept=con))
    
    con = Concept.objects.get(name__iexact="Echocardiography, Four-Dimensional")
    terms = get_termsList(con.id)
    proposed_terms = ["4D echocardiogram", "4-D echocardiogram"]
    for proposed_term in proposed_terms:
        if proposed_term not in terms:
            newTermList.append(Term(name=proposed_term, concept=con))
    
    con = Concept.objects.get(name__iexact="Echocardiography, Transesophageal")
    terms = get_termsList(con.id)
    proposed_terms = ["TEE", "transesophageal echocardiogram", "transesophageal echo"]
    for proposed_term in proposed_terms:
        if proposed_term not in terms:
            newTermList.append(Term(name=proposed_term, concept=con))
    
    con = Concept.objects.get(name__iexact="Myocardial Perfusion Imaging")
    terms = get_termsList(con.id)
    proposed_terms = ["MPI", "cardiac perfusion imaging", "cardiac perfusion image", "cardiac perfusion images", "myocardial perfusion image", "myocardial perfusion images"]
    for proposed_term in proposed_terms:
        if proposed_term not in terms:
            newTermList.append(Term(name=proposed_term, concept=con))
    
    con = Concept.objects.get(name__iexact="Image Interpretation, Computer-Assisted")
    terms = get_termsList(con.id)
    proposed_terms = ["CAD", "computer-assisted diagnosis", "computer assisted diagnosis", "computer-aided diagnosis", "computer aided diagnosis"]
    for proposed_term in proposed_terms:
        if proposed_term not in terms:
            newTermList.append(Term(name=proposed_term, concept=con))
    
    con = Concept.objects.get(name__iexact="Positron-Emission Tomography")
    terms = get_termsList(con.id)
    proposed_terms = ["PET scans", "PET-CT", "PET/CT", "FDG-PET", "FDG PET", "cardiac PET", "PET/MR", "PET-MR", "MR/PET", "MR-PET", "18F-FDG PET"]
    for proposed_term in proposed_terms:
        if proposed_term not in terms:
            newTermList.append(Term(name=proposed_term, concept=con))
    
    con = Concept.objects.get(name__iexact="Tomography, Emission-Computed, Single-Photon")
    terms = get_termsList(con.id)
    proposed_terms = ["single photon emission CT", "single-photon emission computed tomography", "single photon emission computed tomography"]
    for proposed_term in proposed_terms:
        if proposed_term not in terms:
            newTermList.append(Term(name=proposed_term, concept=con))
    
    con = Concept.objects.get(name__iexact="Tomography, X-Ray Computed")
    terms = get_termsList(con.id)
    proposed_terms = ["CT scan", "CAT scan", "CT scans", "CAT scans", "CT image", "CT imaging", "CT images"]
    for proposed_term in proposed_terms:
        if proposed_term not in terms:
            newTermList.append(Term(name=proposed_term, concept=con))
    
    con = Concept.objects.get(name__iexact="Cholangiopancreatography, Magnetic Resonance")
    terms = get_termsList(con.id)
    proposed_terms = ["MRCP", "MR Cholangiopancreatography"]
    for proposed_term in proposed_terms:
        if proposed_term not in terms:
            newTermList.append(Term(name=proposed_term, concept=con))
    
    con = Concept.objects.get(name__iexact="Cholangiopancreatography, Magnetic Resonance")
    terms = get_termsList(con.id)
    proposed_terms = ["Echo-planar imaging", "Echo-planar MR imaging", "Echo-planar image", "Echo-planar MR image", "Echo-planar images", "Echo-planar MR images"]
    for proposed_term in proposed_terms:
        if proposed_term not in terms:
            newTermList.append(Term(name=proposed_term, concept=con))
    
    con = Concept.objects.get(name__iexact="Myelography")
    terms = get_termsList(con.id)
    proposed_terms = ["Myelogram"]
    for proposed_term in proposed_terms:
        if proposed_term not in terms:
            newTermList.append(Term(name=proposed_term, concept=con))
    
    con = Concept.objects.get(name__iexact="Ultrasonography")
    terms = get_termsList(con.id)
    proposed_terms = ["ultrasound", "ultrasound image", "ultrasound images"]
    for proposed_term in proposed_terms:
        if proposed_term not in terms:
            newTermList.append(Term(name=proposed_term, concept=con))
    
    con = Concept.objects.get(name__iexact="Ultrasonography, Mammary")
    terms = get_termsList(con.id)
    proposed_terms = ["breast ultrasound", "breast ultrasonography", "breast US"]
    for proposed_term in proposed_terms:
        if proposed_term not in terms:
            newTermList.append(Term(name=proposed_term, concept=con))
    
    con = Concept.objects.get(name__iexact="Ultrasonography, Interventional")
    terms = get_termsList(con.id)
    proposed_terms = ["interventional ultrasound", "interventional US", "US-guided"]
    for proposed_term in proposed_terms:
        if proposed_term not in terms:
            newTermList.append(Term(name=proposed_term, concept=con))
            
    Term.objects.bulk_create(newTermList)
    print 'Successfully added ' + str(len(newTermList)) + ' terms.'