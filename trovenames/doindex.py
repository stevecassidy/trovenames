"""Script to perform indexing in parallel"""

from multiprocessing import Pool
import os

from index import TroveIndexBuilder

def build(doc):
    print doc
    base, ext = os.path.splitext(os.path.basename(doc))
    out = os.path.join(options.outdir, base + ".idx")
    TroveIndexBuilder(doc, out=out)

if __name__=='__main__':

    import optparse
    import sys

    parser = optparse.OptionParser()
    parser.add_option("-o", "--outdir", dest="outdir", action="store", default='index',
                      help="output directory for index files")
    parser.add_option("-p", "--processes", dest="processes", type=int, action="store", default=5,
                      help="number of concurrent processes to run")

    (options, args) = parser.parse_args()

    if not os.path.exists(options.outdir):
        os.makedirs(options.outdir)

    pool = Pool(options.processes)

    pool.map(build, args)
