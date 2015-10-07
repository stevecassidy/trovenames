# TroveNames

This module supports work on Named Entity Recognition (NER) on a corpus of data
from the NLA Trove Newspaper collection.  It is part of the Alveo Virtual
Laboratory project to support research in Human Communication Science.

The Trove dataset consists of 155 million articles taken from Trove in 2015. This
is a large dataset (450G uncompressed) and so requires some special handling
to process in reasonable time.  The code in this repository has been written
to handle the data making use of the facilities of the NeCTAR Research Cloud
(based on OpenStack).

The original document format is a single large file with one document per line,
each document is encoded as JSON.

## Configuration

This code uses a configuration file, in particular to access the Swift object
store on the Nectar research cloud.  Copy the file `config.ini.dist` in
the `trovenames` directory to `config.ini` and add your own username and
password.

## Chunking

To facilitate parallel processing on the data we split it into chunks of around
3GB in size.  The script chunk.py does this, ensuring that the file is split
at a newline character so that we don't split any documents.

Individual chunks are then stored on the NeCTAR OpenStack object store (Swift)
so that they can be processed on NeCTAR research cloud VMs.  This is a manual
process using 'swift copy'.

## Indexing

To facilitate access to individual documents we build an index containing the
offset and length of each document in the collection.  This can then be used
to grab individual documents from the chunk files for processing.

The script index.py implements the indexing process. There are classes to build
an index from local files (TroveIndexBuilder) or from files on Swift
(TroveSwiftIndexBuilder).  A class (TroveIndex) is provided to read the generated
index and provide access to the individual documents.  

## Processing Individual documents

Once you have an index, you can iterate over documents to process them, this works
on either local files (TroveIndex) or those stored on Swift (TroveSwiftIndex).  Here's
a code snippet to do that:
```
index = TroveSwiftIndex(indexdir=indexdir)

for docid in index.documents:
    doc = index.get_document(docid)
    # doc is a dictionary with document metadata and text
```

## Named Entity Recognition

The ''scripts'' directory contains python scripts to run the NER process using
the Stanford NLP tools.  This is not as yet ported to use the Swift storage and
relies on local files.  (TODO)

NER results are written to JSON files (sample test/trove-sample-result.json.gz).

## Conversion to rdf

NER results are converted to RDF so that they can be served as linked data.
The script genrdf.py does this job.  Not yet ported to use Swift storage (TODO).

The RDF data is copied to a Swift container (manually) and the script 'deploy/update4s.sh'
is used to load it into a configured 4store triple store on a Nectar VM.

## Web application

A simple web application serves the linked data (from the RDF triple store) running
on a NeCTAR VM.  This script will also serve the individual documents (TODO).
