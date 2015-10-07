"""
A web application to provide an interface to the Trove Named Entity data.

Author: Steve Cassidy <Steve.Cassidy@mq.edu.au>
"""

from bottle import Bottle, template, request, response, static_file, abort
import rdflib
from SPARQLWrapper import SPARQLWrapper, JSON
import json

from index import TroveSwiftIndex
from util import readconfig

config = readconfig()
INDEX_DIR = config.get('default', 'INDEX_DIR')

STATIC_PATH = 'static'
SPARQL_ENDPOINT = config.get('default', 'SPARQL_ENDPOINT')

SPARQL = SPARQLWrapper(SPARQL_ENDPOINT)

application = Bottle()

application.troveindex = TroveSwiftIndex(indexdir=INDEX_DIR)


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
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT distinct ?nameid ?name WHERE {
  ?nameid proc:word "%s" .
  ?nameid foaf:name ?name .
}
        """ % (nameq.lower(),)

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
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>

    SELECT ?name WHERE {
      <http://trove.stevecassidy.net/name/%s> foaf:name ?name .
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

    SELECT ?article ?title ?id WHERE {
      ?article schema:mentions <http://trove.stevecassidy.net/name/%s> .
      ?article dcterms:title ?title .
      ?article dcterms:identifier ?id .
    }
    limit 100
    """ % (nameid,)

    SPARQL.setQuery(query)
    SPARQL.setReturnFormat(JSON)
    results = SPARQL.query().convert()

    articles = []
    for r in results["results"]["bindings"]:
        textlink = "/document/" + r["id"]["value"]
        articles.append({'title': r["title"]["value"], 'textlink': textlink, 'link': r["article"]["value"]})


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
        limitterm = "LIMIT 50"

    name = get_name(nameid)

    query = """
PREFIX schema: <http://schema.org/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
SELECT ?otherperson ?name (count(?name) as ?count) WHERE {
      ?article schema:mentions <http://trove.stevecassidy.net/name/%s> .
    ?article schema:mentions ?otherperson .
    ?article dcterms:title ?articletitle .
    ?otherperson foaf:name ?name .
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

    info = {'namelink': namelink, 'name': name, 'associates': assoc}

    if 'application/json' in request.headers['accept']:
        return info
    else:
        return template('associates.tpl', **info)


@application.get('/document/<docid:int>')
def document(docid):
    """Get full metadata for this document"""

    doc = application.troveindex.get_document(str(docid))
    if doc:
        return doc
    else:
        abort(404, 'Unknown document id: "%s"' % docid)


@application.get('/document/<docid:int>.txt')
def document(docid):
    """Get full text for this document"""

    doc = application.troveindex.get_document(str(docid))
    if doc:
        response.content_type = 'text/plain'
        return doc['fulltext']
    else:
        abort(404, 'Unknown document id: "%s"' % docid)


if __name__=='__main__':


    application.run(debug=True, reloader=True)
