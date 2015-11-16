"""Reload the index from a directory of files"""

import sys

from index import TroveIndex, TroveSwiftIndex

idx = TroveSwiftIndex()

idx.reload(indexdir=sys.argv[1])
