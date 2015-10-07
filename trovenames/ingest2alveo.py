'''Script to ingest Trove data into the Alveo VL'''


from index import TroveSwiftIndex

if __name__=='__main__':

    indexdir = 'index'

    index = TroveSwiftIndex(indexdir=indexdir)

    for docid in index.documents:
        doc = index.get_document(docid)
        # doc is a dictionary with document metadata and text
        print doc['heading'], ':', doc['fulltext'][:20], "..."
