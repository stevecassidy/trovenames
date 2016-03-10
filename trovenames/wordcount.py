'''Script to ingest Trove data into the Alveo VL'''

import sys
from index import TroveSwiftIndex
from util import readconfig

def write(count, wordcount, outfile):
    with open(outfile, 'w') as out:
        for year in sorted(count.keys()):
            out.write("%s, %s, %s\n" % (year, count[year], wordcount[year]))



if __name__=='__main__':

    config = readconfig()
    INTERVAL = int(config.get('default', 'WC_INTERVAL'))

    outfile = sys.argv[1]

    index = TroveSwiftIndex()

    count = dict()
    wordcount = dict()

    n = 0
    for docid in index.documents:
        doc = index.get_document(docid)
        # doc is a dictionary with document metadata and text
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
