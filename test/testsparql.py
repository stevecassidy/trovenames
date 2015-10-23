# this file tests that we can talk to our SPARQL server
# as configured in config.ini

import rdflib
from SPARQLWrapper import SPARQLWrapper, JSON
import json

from trovenames.util import readconfig

config = readconfig()
INDEX_DIR = config.get('default', 'INDEX_DIR')

STATIC_PATH = 'static'
SPARQL_ENDPOINT = config.get('default', 'SPARQL_ENDPOINT')

SPARQL = SPARQLWrapper(SPARQL_ENDPOINT)

query = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX proc: <http://trove.stevecassidy.net/schema/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT distinct ?nameid ?name WHERE {
?nameid proc:word "smith" .
?nameid foaf:name ?name .
}
"""

SPARQL.setQuery(query)
SPARQL.setReturnFormat(JSON)
results = SPARQL.query().convert()

print results
