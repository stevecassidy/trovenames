"""Generate RDF from the output of the NER process"""

import json
import gzip
import rdflib
import hashlib

SO = rdflib.Namespace('http://schema.org/')

SOURCE = rdflib.Namespace('http://trove.stevecassidy.net/source/')
NAME = rdflib.Namespace('http://trove.stevecassidy.net/name/')
PROP = rdflib.Namespace('http://trove.stevecassidy.net/schema/')


WORK = rdflib.Namespace('http://trove.nla.gov.au/ndp/del/article/')
RDF = rdflib.Namespace(u"http://www.w3.org/1999/02/22-rdf-syntax-ns#")
RDFS = rdflib.Namespace(u"http://www.w3.org/2000/01/rdf-schema#")
DC = rdflib.Namespace(u"http://purl.org/dc/terms/")
CC = rdflib.Namespace(u"https://creativecommons.org/ns#")


def ner_records(fd):
    """Read the JSON data in filename, yielding a sequence
    of dictionaries, one per record"""
    
    text = ""
    for line in fd.readlines():
        line = line.strip()
        if line == "}{" or line == "}":
            text += "}"
            d = json.loads(text)
            text = "{"
            yield d
        elif line == "{":
            text = line
        else:
            text += line

def genID(prefix, name):
    """Return a URI for this name"""
    
    m = hashlib.md5()
    m.update(name)
    h = m.hexdigest()
    
    return prefix[h]
    

def genrdf(record, graph):
    """Generate RDF for a single record"""
    
    work = WORK[record['article_id']]
    name = genID(NAME, record['name'])
    source = genID(SOURCE, record['article_source'])

    graph.add((work, RDF.type, CC.Work))
    graph.add((work, DC.created, rdflib.Literal(record['article_date'])))
    graph.add((work, DC.title, rdflib.Literal(record['article_title'])))
    graph.add((work, DC.source, source))
    
    graph.add((name, RDF.type, PROP.Name))
    graph.add((name, RDF.label, rdflib.Literal(record['name'])))
    
    # record the mention
    graph.add((work, SO.mentions, name))

    graph.add((source, RDF.type, DC.Collection))
    graph.add((source, DC.hasPart, work))
    graph.add((source, DC.title, rdflib.Literal(record['article_source'])))
    
    

if __name__=='__main__':
    
    import sys
    input = sys.argv[1]
    graph = rdflib.Graph()
    with gzip.open(input) as fd:
        for d in ner_records(fd):
            genrdf(d, graph)
            
    print graph.serialize(format='turtle')
    