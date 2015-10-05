__author__ = 'steve'

import json
import os
import pickle
import gzip
import sys

from swifttext import SwiftTextContainer


class TroveIndex(object):
    """A Trove Index class that uses an in memory dictionary to store
    the index"""

    def __init__(self, indexfile=None, indexdir=None):

        self._index = dict()
        if indexfile:
            self.read(indexfile)
        elif indexdir:
            for fname in os.listdir(indexdir):
                self.read(os.path.join(indexdir, fname))

    def add_to_index(self, id, offset, length, datafile):
        """Add an entry to the index"""

        self._index[id.strip()] = (int(offset), int(length), datafile.strip())


    def read(self, indexfile):
        """Read the index from a file"""

        print "Reading", indexfile

        with open(indexfile, 'r+b') as infile:
            for line in infile:
                id, offset, length, datafile = line.split(',')
                self.add_to_index(id.strip(), int(offset), int(length), datafile.strip())


    @property
    def documents(self):
        """Return an iterator over the documents in the index"""

        return iter(self._index)

    def get_document(self, id):
        """Get a document from the datafile given
        the document id. Return a Python dictionary
        with the document properties or None if there
        is no valid data at this offset"""

        if not id in self._index:
            return None

        offset, length, datafile = self._index[id]

        with open(datafile) as fd:

            fd.seek(offset)
            line = fd.readline()
            try:
                data = json.loads(line)
            except:
                data = None

        return data



class TroveIndexBuilder(object):
    """Create an index over a Trove data set"""

    def __init__(self, datafile, out='index.idx'):
        """Create a Trove Index containing offsets of each document write it to a file.

        datafile - the name of the source data file, can be gzipped or plain text
        outdir - output directory, default 'index'
        """

        self.datafile = datafile
        self.indexfilename = out

        with open(self.indexfilename, 'w+b') as self.out:
            self._build_index()

    def opendata(self):
        """Open the data file
        """

        if self.datafile.endswith("gz"):
            return gzip.open(self.datafile, 'r+b')
        else:
            return open(self.datafile, 'r+b')


    def add_to_index(self, id, offset, length):
        """Add this id/offset pair to the index
        """

        self.out.write("%s, %d, %d, %s\n" % (id, offset, length, self.datafile))

    def _build_index(self):
        """Build an index of the documents in the datafile
        """

        with self.opendata() as fd:
            done = False
            ln = 0
            while not done:
                offset = fd.tell()
                line = fd.readline()
                try:
                    data = json.loads(line.decode('utf-8'))
                except:
                    done = True
                    continue

                if 'id' in data:
                    id = data['id']
                    self.add_to_index(id, offset, len(line))
                else:
                    print("Bad line: ", line)







class TroveSwiftIndex(TroveIndex):
    """A Trove Index class that uses an in memory dictionary to store
    the index - for access to data stored in a Swift container"""

    def __init__(self, indexfile=None, indexdir=None):

        self.swifttext = SwiftTextContainer()

        super(TroveSwiftIndex, self).__init__(indexfile, indexdir)

    def get_document(self, id):
        """Get a document from the datafile given
        the document id. Return a Python dictionary
        with the document properties or None if there
        is no valid data at this offset"""

        if not id in self._index:
            return None

        offset, length, datafile = self._index[id]

        line = self.swifttext.get_by_offset(datafile, offset, length)

        try:
            data = json.loads(line)
        except:
            data = None

        return data


class TroveSwiftIndexBuilder(TroveIndexBuilder):
    """Build an index for documents stored in a Swift object store"""


    def __init__(self, datafile, out='index.idx'):
        """Create a Trove Index containing offsets of each document write it to a file.

        datafile - the name of the source data file, can be gzipped or plain text
        outdir - output directory, default 'index'
        """

        self.swifttext = SwiftTextContainer()
        self.datafile = datafile

        super(TroveSwiftIndexBuilder, self).__init__(datafile, out)


    def _build_index(self):
        """Build an index of the documents in the datafile
        """

        for offset, line in self.swifttext.document_lines(self.datafile):

            try:
                data = json.loads(line.decode('utf-8'))
            except:
                done = True
                continue

            if 'id' in data:
                id = data['id']
                self.add_to_index(id, offset, len(line))
            else:
                print("Bad line: ", line)




if __name__=='__main__':

    import optparse
    import sys

    parser = optparse.OptionParser()
    parser.add_option("-o", "--outdir", dest="outdir", action="store", default='index',
                      help="output directory for index files")

    (options, args) = parser.parse_args()

    if len(args) != 0:
        parser.print_help(sys.stdout)
        exit()

    container = SwiftTextContainer()

    if not os.path.exists(options.outdir):
        os.makedirs(options.outdir)

    for doc in container.documents():
        base, ext = os.path.splitext(doc['name'])
        out = os.path.join(options.outdir, base + ".idx")
        TroveSwiftIndexBuilder(doc['name'], out=out)
