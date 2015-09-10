__author__ = 'steve'

import json
import os
import sys
import pickle
import gzip
import argparse


chunks = []

def build_index(input_file, chunksize):
	"""Build an index of the documents in the datafile
			index consists of:
		{<docid>: (<docoffset>, <doclength>),
		...}
	"""

	print 'building index on ' + input_file + 'with chunksize: ' + str(chunksize)

	index = dict()
	with gzip.open(input_file, 'r+b') as fd:
		done = False
		ln = 0
		while not done:
			offset = fd.tell()
			line = fd.readline()
			try:
				data = json.loads(line.decode('utf-8'))
			except:
				done = True

			if 'id' in data:
				id = data['id']
				index[id] = offset
			else:
				print("Bad line: ", line)

			# record a chunk if we hit chunksize lines
			if ln != 0 and ln % chunksize == 0:
				if chunks == []:
					start = 0
				else:
					start = chunks[-1][0] + chunks[-1][1]
				size = offset-start
				chunks.append((start, size))
			ln += 1
		# record the final chunk
		if len(chunks) > 0:
			start = chunks[-1][0] + chunks[-1][1]
		else:
			start = 0
		size = fd.tell()-start
		if size > 0:
			chunks.append((start, size))


def write(output_file):
	"""Write a copy of the index to a file
	with the same name as the data file + .idx"""

	with open(output_file, 'w+b') as out:
		pickle.dump(chunks, out)



if __name__=='__main__':

	parser = argparse.ArgumentParser(description='Generate index data.')
	parser.add_argument('--input_data_file', metavar='file', dest='input_data_file', help='Input data file')
	parser.add_argument('--chunksize', metavar='int', dest='chunksize', help='Chunk size for splitting data files')
	parser.add_argument('--out_idx_file', metavar='file', dest='out_idx_file', help='Output index file')
	args = parser.parse_args()

	build_index(args.input_data_file, int(args.chunksize))
	write(args.out_idx_file)








