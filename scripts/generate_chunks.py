__author__ = 'steve'


import os
import sys
import pickle
import gzip
import argparse


if __name__=='__main__':

	parser = argparse.ArgumentParser(description='Generate chunk data.')
	parser.add_argument('--input_idx_file', metavar='file', dest='input_idx_file', help='Input index file')
	parser.add_argument('--input_data_file', metavar='file', dest='input_data_file', help='Input data file')
	parser.add_argument('--out_dir', metavar='dir', dest='out_dir', help='Output chunk directory')
	args = parser.parse_args()
	
	# args.input_idx_file = '/home/sunghwan/workspace/ner_project/data/trove/data_10M.idx'
	with open(args.input_idx_file, 'r+b') as infile:
		chunks = pickle.load(infile)
		print '(offset, size) list: ' 
		print chunks

	if not os.path.exists(args.out_dir):
		os.makedirs(args.out_dir)

	fd = gzip.open(args.input_data_file, 'r+b')
	n = 1
	for offset, size in chunks:
		write_size = 10000000
		print "offset: %d, size: %d" % (offset, size)
		name, ext = os.path.splitext(os.path.basename(args.input_data_file))
		name += "-%d" % n
		n += 1

		chunk_size = offset + size
		with open(os.path.join(args.out_dir, name), 'w+b') as out:
			fd.seek(offset)
			for i in xrange(offset, chunk_size, write_size):				
				if (chunk_size-i) >= write_size:
					out.write(fd.read(write_size))
				else:				
					out.write(fd.read(chunk_size-i))
				sys.stdout.write('.')

