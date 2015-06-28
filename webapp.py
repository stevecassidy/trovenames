"""
A web application to provide an interface to the Trove Named Entity data.

Author: Steve Cassidy <Steve.Cassidy@mq.edu.au>
"""

from bottle import Bottle, template, request, response, static_file, abort
import rdflib
from SPARQLWrapper import SPARQLWrapper, JSON

STATIC_PATH = 'static'
SPARQL_ENDPOINT = 'http://trove.stevecassidy.net/sparql/'

SPARQL = SPARQLWrapper(SPARQL_ENDPOINT)


application = Bottle()

@application.get('/static/<path:path>')
def static_files(path):
    return static_file(path, root=STATIC_PATH)


@application.get('/')
def index():
	"""Main index page"""
	
	return template('index.tpl')
	
@application.get('/about')
def about():
	"""An about page"""
	
	return template('about.tpl')
	
@application.get('/query')
def query():
	"""The YASGUI query page"""
	
	return template('sparql.tpl', endpoint=SPARQL_ENDPOINT)

@application.get('/source/<sourceid>')
def source(sourceid):
	"""Return information about this source"""
	
	query = """
	PREFIX dcterms: <http://purl.org/dc/terms/>
	SELECT ?title WHERE { 
	  <http://trove.stevecassidy.net/source/%s> dcterms:title ?title .
	}
	""" % (sourceid,)
	
	SPARQL.setQuery(query)
	SPARQL.setReturnFormat(JSON)
	results = SPARQL.query().convert()
 
 	if len(results["results"]["bindings"]) > 0:
		result = results["results"]["bindings"][0]
		title = result["title"]["value"]
	else:
		# 404
		abort(404, 'Unknown source id: "%s"' % sourceid)
	
	query = """
	PREFIX dcterms: <http://purl.org/dc/terms/>
	SELECT ?article WHERE {
	  <http://trove.stevecassidy.net/source/%s> dcterms:hasPart ?article .
	}
	""" % (sourceid,)
	
	SPARQL.setQuery(query)
	SPARQL.setReturnFormat(JSON)
	results = SPARQL.query().convert()
	
 	if len(results["results"]["bindings"]) > 0:
		articles = [r["article"]["value"] for r in results["results"]["bindings"]]
	else:
		articles = []
	
	return {'title': title, 'id': sourceid, 'articles': articles}
	

def get_name(nameid):
	"""Get the name of this nameid"""
	
	
	query = """
	PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
	SELECT ?name WHERE { 
	  <http://trove.stevecassidy.net/name/%s> rdf:label ?name .
	}
	""" % (nameid,)
	
	SPARQL.setQuery(query)
	SPARQL.setReturnFormat(JSON)
	results = SPARQL.query().convert()
 
 	if len(results["results"]["bindings"]) > 0:
		result = results["results"]["bindings"][0]
		name = result["name"]["value"]
	else:
		# 404
		abort(404, 'Unknown name id: "%s"' % nameid)
		
		
	return name


@application.get('/name/<nameid>')
def name(nameid):
	"""Return information about this name"""
	
	name = get_name(nameid)
	
	query = """
	PREFIX schema: <http://schema.org/>
	SELECT ?article WHERE {
	  ?article schema:mentions <http://trove.stevecassidy.net/name/%s> .
	}
	""" % (nameid,)
	
	SPARQL.setQuery(query)
	SPARQL.setReturnFormat(JSON)
	results = SPARQL.query().convert()
	
 	if len(results["results"]["bindings"]) > 0:
		articles = [r["article"]["value"] for r in results["results"]["bindings"]]
	else:
		articles = []	
	
	alink = "http://trove.stevecassidy.net/associates/%s" % (nameid,)
	namelink = "http://trove.stevecassidy.net/name/%s" % (nameid,)
	
	return {'id': namelink, 'name': name, 'mentioned_in': articles, 'associates': alink }


@application.get('/associates/<nameid>')
def associates(nameid):
	"""Return a list of the 'associates' of this nameid, associates
	are mentioned in the same article as this person"""


	if 'limit' in request.GET:
		limitterm = "LIMIT %d" % int(request.GET['limit'])
	else:
		limitterm = ""

	name = get_name(nameid)

	query = """
PREFIX schema: <http://schema.org/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dcterms: <http://purl.org/dc/terms/>
SELECT ?otherperson ?name (count(?name) as ?count) WHERE {
  	?article schema:mentions <http://trove.stevecassidy.net/name/%s> .
    ?article schema:mentions ?otherperson .
    ?article dcterms:title ?articletitle .
    ?otherperson rdf:label ?name .
  filter (<http://trove.stevecassidy.net/name/%s> != ?otherperson)
} group by ?name
order by desc(?count)
	""" % (nameid, nameid)
	
	query = query + limitterm

	SPARQL.setQuery(query)
	SPARQL.setReturnFormat(JSON)
	results = SPARQL.query().convert()
	
	assoc = []
 	for binding in results["results"]["bindings"]:
		d = {'name': binding["name"]["value"],
			 'url': binding["otherperson"]["value"],
		 	 'count': binding["count"]["value"]}
		assoc.append(d)
		

	namelink = "http://trove.stevecassidy.net/name/%s" % (nameid,)
	
	return {'id': namelink, 'name': name, 'associates': assoc}

	
	
	
if __name__=='__main__':
	
	application.run(debug=True, reloader=True)