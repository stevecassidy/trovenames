"""Generate RDF from the output of the NER process"""

import json
import gzip
import rdflib
import hashlib
import string

from rdflib.namespace import XSD

SO = rdflib.Namespace('http://schema.org/')

SOURCE = rdflib.Namespace('http://trove.alveo.edu.au/source/')
NAME = rdflib.Namespace('http://trove.alveo.edu.au/name/')
PROP = rdflib.Namespace('http://trove.alveo.edu.au/schema/')
FULLTEXT = rdflib.Namespace('http://trove.alveo.edu.au/document/')


FOAF = rdflib.Namespace('http://xmlns.com/foaf/0.1/')
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
        line = line.strip().decode('utf-8')
        if line == "},{" or line == "}":
            text += "}"
            d = json.loads(text)
            text = "{"
            yield d
        elif line == "[" or line == "]":
            pass
        elif line == "{":
            text = line
        else:
            text += line

def genID(prefix, name):
    """Return a URI for this name"""

    m = hashlib.md5()
    m.update(name.encode())
    h = m.hexdigest()

    return prefix[h]

def normalise_name(name):
    """Return a normalised version of this name"""

    return string.capwords(name)



def genrdf(record, graph):
    """Generate RDF for a single record"""

    work = WORK[record['article_id']]
    name = genID(NAME, normalise_name(record['name']))
    source = genID(SOURCE, record['article_source'])

    graph.add((work, RDF.type, CC.Work))
    graph.add((work, DC.created, rdflib.Literal(record['article_date'])))
    graph.add((work, DC.title, rdflib.Literal(record['article_title'])))
    graph.add((work, DC.source, source))
    graph.add((work, DC.identifier, rdflib.Literal(record['article_id'])))
    graph.add((work, PROP.fulltext, FULLTEXT[record['article_id']+".txt"]))

    # TODO: add article year
    year = int(record['article_date'][0:4])
    graph.add((work, PROP.year, rdflib.Literal(year)))

    graph.add((name, RDF.type, PROP.Name))
    # add the normalised name as FOAF.name properties
    graph.add((name, FOAF.name, rdflib.Literal(normalise_name(record['name']))))
    # add the individual words in the name to help query
    for word in record['name'].split():
        graph.add((name, PROP.word, rdflib.Literal(word.lower())))
    lastname = record['name'].split()[-1]
    graph.add((name, FOAF.family_name, rdflib.Literal(lastname.lower())))

    # record the mention
    graph.add((work, SO.mentions, name))
    graph.add((work, PROP.context, rdflib.Literal(record['name_context'])))


    graph.add((source, RDF.type, DC.Collection))
    graph.add((source, DC.hasPart, work))
    graph.add((source, DC.title, rdflib.Literal(record['article_source'])))


def process_files(files, outdir, prefix="trovenames", threshold=1000000):
    """Turn these files into RDF"""


    graph = rdflib.Graph()
    records = 0
    outcount = 1
    for datafile in files:
        print(datafile)
        with gzip.open(datafile) as fd:
            for d in ner_records(fd):
                genrdf(d, graph)
                if records > threshold:
                    output_graph(graph, prefix + "-" + str(outcount), outdir)
                    records = 0
                    outcount += 1
                    # remove everything from the graph now we've written it out
                    graph = rdflib.Graph()
                else:
                    records += 1

        # finish off
        output_graph(graph, prefix + "-" + str(outcount), outdir)



def output_graph(graph, basename, outdir):
    """Write this graph out to the right place"""

    graph.bind('dcterms', DC)
    graph.bind('schema', SO)
    graph.bind('cc', CC)
    graph.bind('trovenames', PROP)
    graph.bind('foaf', FOAF)

    turtle = graph.serialize(format='turtle')

    outfile = os.path.join(outdir, basename + ".ttl")
    with open(outfile, 'w') as out:
        out.write(turtle.decode('utf-8'))

    print "\t>> ", outfile

    return outfile


if __name__=='__main__':

    import sys, os
    import argparse

    parser = argparse.ArgumentParser(description='convert NER output to RDF')
    parser.add_argument('--outdir', default='results', help='directory for output files')
    parser.add_argument('files', metavar='files', nargs='+', help='input data files')
    args = parser.parse_args()

    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)

    process_files(args.files, args.outdir)
