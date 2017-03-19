'''Script to ingest Trove data into the Alveo VL'''

import sys
import json
from swifttext import SwiftTextContainer
from util import readconfig
from multiprocessing import Pool

def write(count, wordcount, outfile):
    with open(outfile, 'w') as out:
        out.write("year, documents, words\n")
        for year in sorted(count.keys()):
            out.write("%s, %s, %s\n" % (year, count[year], wordcount[year]))

def countwords(document):

    #print "COUNT", document


    docname = document['name']

    outfile = "wordcount-" + docname

    sw = SwiftTextContainer()

    count = dict()
    wordcount = dict()

    n = 0
    for offset,line in sw.document_lines(docname):

        try:
            doc = json.loads(line.decode('utf-8'))
        except:
            sys.stdout.write('!*!')
            sys.stdout.flush()
            continue

        try:
            year = doc['date'][:4]
            wc = int(doc['wordCount'])
            if year in count:
                count[year] += 1
            else:
                count[year] = 0

            if year in wordcount:
                wordcount[year] += wc
            else:
                wordcount[year] = wc

            n += 1

            if n % INTERVAL == 0:
                write(count, wordcount, outfile)
                sys.stdout.write("%s|" % n)
                sys.stdout.flush()
        except:
            pass


if __name__=='__main__':

    config = readconfig()
    INTERVAL = int(config.get('default', 'WC_INTERVAL'))
    processes = int(config.get('default', 'PROCESSES'))

    sw = SwiftTextContainer()

    pool = Pool(processes)

    pool.map(countwords, sw.documents())
