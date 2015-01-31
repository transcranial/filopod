from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Domain(models.Model):
	name = models.CharField(max_length=20)
	datetime_added = models.DateTimeField(auto_now_add=True)

class Ontology(models.Model):
	name = models.CharField(max_length=20)
	domain = models.ManyToManyField(Domain, blank=True, null=True)
	datetime_added = models.DateTimeField(auto_now_add=True)

class Concept(models.Model):
	name = models.CharField(max_length=500)
	type = models.CharField(max_length=50)
	ontology = models.ForeignKey(Ontology, blank=True, null=True)
	conceptID = models.CharField(max_length=255, unique=True, blank=True, null=True)
	datetime_added = models.DateTimeField(auto_now_add=True)

class Term(models.Model):
	name = models.CharField(max_length=500)
	concept = models.ForeignKey(Concept)
	datetime_added = models.DateTimeField(auto_now_add=True)
	
class ConceptConceptLink(models.Model):
	user = models.ForeignKey(User, blank=True, null=True)
	source_concept = models.ForeignKey(Concept, related_name='source')
	target_concept = models.ForeignKey(Concept, related_name='target')
	type = models.CharField(max_length=50)
	value = models.DecimalField(default=0, max_digits=10, decimal_places=9)
	datetime_added = models.DateTimeField(auto_now_add=True)
	
class Resource(models.Model):
	identifier = models.CharField(max_length=500, blank=True, null=True)
	user = models.ManyToManyField(User, blank=True, null=True)
	domain = models.ManyToManyField(Domain, blank=True, null=True)
	type = models.CharField(max_length=20, blank=True, null=True)
	language = models.CharField(max_length=2, blank=True, null=True)
	title = models.CharField(max_length=300, blank=True, null=True)
	date = models.CharField(max_length=20, blank=True, null=True)
	publisher = models.CharField(max_length=100, blank=True, null=True)
	author = models.CharField(max_length=767, blank=True, null=True)
	journal = models.CharField(max_length=50, blank=True, null=True)
	volume = models.CharField(max_length=10, blank=True, null=True)
	issue = models.CharField(max_length=10, blank=True, null=True)
	firstpage = models.CharField(max_length=10, blank=True, null=True)
	lastpage = models.CharField(max_length=10, blank=True, null=True)
	url = models.URLField(blank=True, null=True)
	html_source = models.TextField(blank=True, null=True)
	datetime_added = models.DateTimeField(auto_now_add=True)
	
class Subresource(models.Model):
	containing_resource = models.ForeignKey(Resource)
	concepts_contained = models.ManyToManyField(Concept, blank=True, null=True)
	name = models.CharField(max_length=50, blank=True, null=True)
	# type, e.g. sentence, paragraph, figure
	type = models.CharField(max_length=10, blank=True, null=True)
	content = models.TextField(blank=True, null=True)
	url = models.URLField(blank=True, null=True)
	datetime_added = models.DateTimeField(auto_now_add=True)
	
class MatrixFiles(models.Model):
	name = models.CharField(max_length=20, blank=True, null=True)
	user = models.ManyToManyField(User, blank=True, null=True)
	type = models.CharField(max_length=50)
	path = models.CharField(max_length=500, blank=True, null=True)

class Plan(models.Model):
	stripe_plan_id = models.CharField(max_length=50)
	name = models.CharField(max_length=500)
	description = models.TextField()
	price = models.DecimalField(max_digits=10, decimal_places=2)
	currency = models.CharField(max_length=10)
	interval = models.PositiveIntegerField() #in months
	resources = models.PositiveIntegerField()
	user = models.ManyToManyField(User, blank=True, null=True)