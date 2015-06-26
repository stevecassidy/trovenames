"""
A web application to provide an interface to the Trove Named Entity data.

Author: Steve Cassidy <Steve.Cassidy@mq.edu.au>
"""

from bottle import Bottle, template, request, response, static_file, abort
import rdflib
from SPARQLWrapper import SPARQLWrapper, JSON

STATIC_PATH = 'static'
SPARQL_ENDPOINT = 'http://144.6.227.157/sparql/'

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
	
	
@application.get('/name/<nameid>')
def name(nameid):
	"""Return information about this name"""
	
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
	
	return {'id': nameid, 'name': name, 'mentioned_in': articles }
	
	
if __name__=='__main__':
	
	application.run(debug=True, reloader=True)