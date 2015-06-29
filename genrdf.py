"""Generate RDF from the output of the NER process"""

import json
import gzip
import rdflib
import hashlib

from rdflib.namespace import XSD

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
    
    # TODO: add article year
    year = int(record['article_date'][0:4])
    graph.add((work, PROP.year, rdflib.Literal(year)))
    
    graph.add((name, RDF.type, PROP.Name))
    graph.add((name, RDF.label, rdflib.Literal(record['name'])))
    for word in record['name'].split():
        graph.add((name, PROP.word, rdflib.Literal(word.lower())))
    lastname = record['name'].split()[-1]
    graph.add((name, PROP.lastname, rdflib.Literal(lastname.lower())))
    
    # record the mention
    graph.add((work, SO.mentions, name))
    graph.add((work, PROP.context, rdflib.Literal(record['name_context'])))


    graph.add((source, RDF.type, DC.Collection))
    graph.add((source, DC.hasPart, work))
    graph.add((source, DC.title, rdflib.Literal(record['article_source'])))
    
    

if __name__=='__main__':
    
    import sys, os
    import argparse
    
    parser = argparse.ArgumentParser(description='convert NER output to RDF')
    parser.add_argument('--outdir', default='results', help='directory for output files')
    parser.add_argument('files', metavar='files', nargs='+', help='input data files')
    args = parser.parse_args()
    
    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)

    for datafile in args.files:
        graph = rdflib.Graph()
        with gzip.open(datafile) as fd:
            for d in ner_records(fd):
                genrdf(d, graph)
            
            
        graph.bind('dcterms', DC)
        graph.bind('schema', SO)
        graph.bind('cc', CC)
        graph.bind('trovenamesq', PROP)
        #graph.bind('source', SOURCE)
            
        turtle = graph.serialize(format='turtle')
        
        basename, ext = os.path.splitext(os.path.splitext(datafile)[0])
        
        print os.path.join(args.outdir, basename + ".ttl")
        with open(os.path.join(args.outdir, basename + ".ttl"), 'w') as out:
            out.write(turtle)
        
        
        
    