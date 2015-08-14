__author__ = 'steve'

import json
import os
import pickle
import gzip
import redis

class TroveIndex:
    """An index over a Trove data set"""


    def __init__(self, datafile, chunksize=1000000, force=False, buildindex=True):
        """Create a Trove Index instance containing offsets of
        chunks of lines and optionally of each document.

        datafile - the name of the source data file, can be gzipped or plain text
        chunksize - the size of chunks to locate in the file
           (default 1000000)
        force - if True, the index and chunk lists are recomputed even if a stored
                 version is found (default False)
        buildindex - if True, we build a document index, if False only chunk index is built
           (default True)

        """


        self.datafile = datafile
        self.buildindex = buildindex
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)


        if not force and os.path.exists(self.indexfilename):
            self.read()
        else:
            self._build_index(chunksize)
            self.write()

    @property
    def chunks(self):
        """Return a list of the chunks from the file
        as a list of (start, size) tuples"""
        return self._chunks


    def documents(self):
        """Return an iterator over the document ids
        stored in the index"""

        return iter(self._index)


    @property
    def indexfilename(self):

        return self.datafile + ".idx"


    def write(self):
        """Write a copy of the index to a file
        with the same name as the data file + .idx"""

        filename = self.indexfilename

        with open(filename, 'w+b') as out:
            pickle.dump([self.datafile, self._index, self._chunks], out)

    def read(self):
        """Read the index from a file"""

        filename = self.indexfilename

        with open(filename, 'r+b') as infile:
            df, idx, ch = pickle.load(infile)
            self.datafile = df
            self._index = idx
            self._chunks = ch

    def opendata(self):
        """Open the data file"""

        if self.datafile.endswith("gz"):
            return gzip.open(self.datafile, 'r+b')
        else:
            return open(self.datafile, 'r+b')

    def add_to_index(self, id, offset):
        """Add this id/offset pair to the index"""

        self._index[id] = offset
        self.redis.set(id, offset)


    def _build_index(self, chunksize):
        """Build an index of the documents in the datafile

            index consists of:
            {<docid>: (<docoffset>, <doclength>),
            ...}
        """

        self._index = dict()
        self._chunks = []

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

                if self.buildindex:
                    if 'id' in data:
                        id = data['id']
                        self.add_to_index(id, offset)
                    else:
                        print("Bad line: ", line)

                # record a chunk if we hit chunksize lines
                if ln != 0 and ln % chunksize == 0:
                    if self._chunks == []:
                        start = 0
                    else:
                        start = self._chunks[-1][0] + self._chunks[-1][1]
                    size = offset-start
                    self._chunks.append((start, size))
                ln += 1
            # record the final chunk
            if len(self._chunks) > 0:
                start = self._chunks[-1][0] + self._chunks[-1][1]
            else:
                start = 0
            size = fd.tell()-start
            if size > 0:
                self._chunks.append((start, size))

    def get_document(self, id):
        """Get a document from the datafile given
        the document id. Return a Python dictionary
        with the document properties or None if there
        is no valid data at this offset"""

        if not id in self._index:
            return None

        #offset = self._index[id]
        offset = int(self.redis.get(id))

        with open(self.datafile) as fd:

            fd.seek(offset)
            line = fd.readline()
            try:
                data = json.loads(line)
            except:
                data = None

        return data


    def write_chunks(self, outdir):
        """Write out chunks of the original data file
        to separate files in the directory outdir"""

        if not os.path.exists(outdir):
            os.makedirs(outdir)

        n = 1
        write_size = 10000
        with self.opendata() as fd:
            for offset, size in self.chunks:
                name, ext = os.path.splitext(os.path.basename(self.datafile))
                name += "-%d" % n + ext
                n += 1
                chunk_size = offset + size
                with open(os.path.join(outdir, name), 'w+b') as out:
                        fd.seek(offset)
                        i_prv = 0
                        for i in range(offset, chunk_size, write_size):
                                if (chunk_size-i) >= write_size:
                                        out.write(fd.read(write_size))
                                else:
                                        out.write(fd.read(chunk_size-i))
                                sys.stdout.write('.')
                sys.stdout.write('|')
        print()



    def wsgi(self):
        """Return a WSGI application procedure to serve files from the
        data set.

        GET /document/<id> returns the whole JSON for this document
        GET /document/<id>.txt returns the document text
        """


        def application(environ, start_response):
            """WSGI Procedure"""

            docmatch = re.match(r'/document/([0-9]+$)', environ['PATH_INFO'])
            txtmatch = re.match(r'/document/([0-9]+)\.txt$', environ['PATH_INFO'])
            if docmatch:
                id = docmatch.group(1)
                doc = self.get_document(id)
                if doc:
                    jsontext = json.dumps(doc)
                    status = '200 OK'
                    headers = [('Content-type', 'application/json')]
                    start_response(status, headers)
                    return [jsontext.encode('utf-8')]
            elif txtmatch:
                id = txtmatch.group(1)
                doc = self.get_document(id)
                if doc:
                    text = doc['fulltext']
                    status = '200 OK'
                    headers = [('Content-type', 'text/plain')]
                    start_response(status, headers)
                    return [text.encode('utf-8')]

            # if we get here then it's a 404
            status = '404 Not Found'
            headers = [('Content-type', 'text/plain')]
            start_response(status, headers)
            return [s.encode('utf-8') for s in ["Page Not Found\n",
                    "Serving Trove data from %s\n" % self.datafile,
                    "Total of %d unique documents.\n" % len(self._index)
                    ]]

        return application

import re

if __name__=='__main__':

    import optparse
    import sys

    parser = optparse.OptionParser()
    parser.add_option("-c", "--chunksize",
                      action="store", dest="chunksize", type=int, default=1000000,
                      help="Chunk size for splitting data files, default 1000000")
    parser.add_option("-w", "--writechunks", dest="outdir", action="store", default=None,
                      help="write split files out to OUTDIR")
    parser.add_option("-n", "--nodocindex", dest="docindex", action="store_false", default=True,
                      help="don't build the document index (only chunks)")
    parser.add_option("-f", "--force", dest="force", action="store_true", default=False,
                      help="force re-indexing of data even if there is a stored index")
    parser.add_option("-s", "--serve", dest="serve", action="store_true", default=False,
                      help="start a web server to serve documents")

    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.print_help(sys.stdout)
        exit()
    filename = args[0]

    index = TroveIndex(filename, chunksize=options.chunksize, force=options.force)

    if options.outdir:
        index.write_chunks(options.outdir)


    if options.serve:
        from wsgiref.simple_server import make_server

        port = 3333
        server = make_server('localhost', port, index.wsgi())
        print("Listening on http://localhost:"+str(port) + "/")
        server.serve_forever()