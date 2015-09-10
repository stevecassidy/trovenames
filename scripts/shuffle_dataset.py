#!/usr/bin/python

## read randomly selected Json format articles using extract_randomTrove.py
## shuffle and dived them to generate datasets

import io
import re
import string
import json
import math
import random
from bs4 import BeautifulSoup
from random import shuffle

def readData(filename):
	infile = open(filename)
	json_objects = json.load(infile)
	infile.close()
	return json_objects


# Fisher-Yates-Durstenfeld shuffle
def shuffleData(data):
	data_length = len(data)
	for n in xrange(data_length):
		k = int(n + math.floor(random.random() * (data_length-n)))
		temp = data[k]
		data[k] = data[n]
		data[n] = temp
	return data

def writeOut(name, data):
	with io.open(name, 'w', encoding='utf-8') as outfile:
		for json_object in data:
			outfile.write(unicode(json.dumps(json_object, indent=4, ensure_ascii=False)))
	outfile.close()	

def divideData(data, dev_file, heldout_file, test_file):
	# 200 articles for each dataset
	writeOut(dev_file, data[0:200])
	writeOut(heldout_file, data[200:400])
	writeOut(test_file, data[400:600])



if __name__ == "__main__":
	import argparse
	
	parser = argparse.ArgumentParser(description='Shuffle and divide randomly chosen Trove data.')
	parser.add_argument('--input_file', metavar='file', dest='input_file', help='Trove random data file')
	parser.add_argument('--dev_file', metavar='file', dest='dev_file', help='dev data file')
	parser.add_argument('--heldout_file', metavar='file', dest='heldout_file', help='heldout data file')	
	parser.add_argument('--test_file', metavar='file', dest='test_file', help='test data file')
	args = parser.parse_args()
	
	# input_file = "../data/trove/data_0.9_5.json"
	# dev_file = "../data/trove/dev_200.json"
	# heldout_file = "../data/trove/heldout_200.json"
	# test_file = "../data/trove/test_200.json"

	dataset = readData(args.input_file)
	dataset = shuffleData(dataset)
	divideData(dataset, args.dev_file, args.heldout_file, args.test_file)
	

