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

@application.get('/name')
def searchnames():
	"""Present a user form to query names"""

	if 'name' in request.GET:
		nameq = request.GET['name']
		
		query = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX proc: <http://trove.stevecassidy.net/schema/>

SELECT distinct ?nameid ?name WHERE {
  ?nameid proc:word "%s" .
  ?nameid rdf:label ?name .
}
		""" % (nameq,)
		
		print "QUERY: ", query
		
		SPARQL.setQuery(query)
		SPARQL.setReturnFormat(JSON)
		results = SPARQL.query().convert()

		links = []
		for result in results["results"]["bindings"]:
			links.append({'link': result["nameid"]["value"], 'name': result["name"]["value"]})
		
		return template('namesearch.tpl', links=links)
	
	else:
		return template('namesearch.tpl', links=[])
		
		

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
	prefix dcterms: <http://purl.org/dc/terms/>
	
	SELECT ?article ?title WHERE {
	  ?article schema:mentions <http://trove.stevecassidy.net/name/%s> .
	  ?article dcterms:title ?title
	}
	limit 50
	""" % (nameid,)
	
	SPARQL.setQuery(query)
	SPARQL.setReturnFormat(JSON)
	results = SPARQL.query().convert()
	
	articles = []	
	for r in results["results"]["bindings"]:
		print "ROW", r
		articles.append({'title': r["title"]["value"], 'link': r["article"]["value"]})
		
	
	alink = "/associates/%s" % (nameid,)
	namelink = "/name/%s" % (nameid,)
		
	info = {'namelink': namelink, 'name': name, 'mentioned_in': articles, 'associates': alink }

	
	if 'application/json' in request.headers['accept']:
		return info
	else:
		return template('name.tpl', **info)


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
limit 50
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
	
	info = {'namelink': namelink, 'name': name, 'associates': assoc}

	if 'application/json' in request.headers['accept']:
		return info
	else:
		return template('associates.tpl', **info)	
	
	
if __name__=='__main__':
	
	application.run(debug=True, reloader=True)