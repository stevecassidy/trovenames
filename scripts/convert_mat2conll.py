#!/usr/bin/python

## convert the output of MAT annotation tool into Conll format for Stanford NER

import os
import re
import nltk
from nltk.tokenize import *
import json
from pprint import pprint
from os import listdir
from os.path import isfile, join

is_debugging = False

def writeConll(mat_path, mat_file, conll_path):
	infile = mat_path + mat_file
	print infile

	with open(infile) as f:
		data = json.load(f)

	per_idx = []
	org_idx = []
	loc_idx = []
	annot_idx = []
	for i in xrange(len(data["asets"])):
		if data["asets"][i]["type"] == "PERSON":
			per_idx = data["asets"][i]["annots"]
		elif data["asets"][i]["type"] == "ORGANIZATION":
			org_idx = data["asets"][i]["annots"]
		elif data["asets"][i]["type"] == "LOCATION":
			loc_idx = data["asets"][i]["annots"]
		elif data["asets"][i]["type"] == "lex":
			annot_idx = data["asets"][i]["annots"]
	raw_sent = data["signal"]

	if annot_idx is not None:
		outfile = conll_path + os.path.splitext(mat_file)[0] + ".conll"
		output_file = open(outfile, 'w')
		for word_idx in annot_idx:
			ner_tag = "O"
			st_idx = word_idx[0]
			end_idx = word_idx[1]
			word = raw_sent[st_idx:end_idx]		
			is_detected = False
			if per_idx is not None:		
				for p_idx in per_idx:
					if st_idx==p_idx[0]:
						if is_debugging:
							print "%s \t B-PER" % word
						ner_tag = "PERSON"
						is_detected = True
						break
					elif (st_idx>p_idx[0]) & (end_idx<=p_idx[1]):
						if is_debugging:
							print "%s \t I-PER" % word
						ner_tag = "PERSON"
						is_detected = True
						break				
				if is_detected:
					output_file.write(word.encode('utf-8') + "\t" + ner_tag + "\n")		
					continue

			if org_idx is not None:
				for o_idx in org_idx:
					if st_idx==o_idx[0]:
						if is_debugging:
							print "%s \t B-ORG" % word
						ner_tag = "ORGANIZATION"
						is_detected = True
						break
					elif (st_idx>o_idx[0]) & (end_idx<=o_idx[1]):
						if is_debugging:
							print "%s \t I-ORG" % word
						ner_tag = "ORGANIZATION"
						is_detected = True
						break				
				if is_detected:
					output_file.write(word.encode('utf-8') + "\t" + ner_tag + "\n")		
					continue
			if loc_idx is not None:	
				for l_idx in loc_idx:
					if st_idx==l_idx[0]:
						if is_debugging:
							print "%s \t B-LOC" % word
						ner_tag = "LOCATION"
						is_detected = True
						break
					elif (st_idx>l_idx[0]) & (end_idx<=l_idx[1]):
						if is_debugging:
							print "%s \t I-LOC" % word
						ner_tag = "LOCATION"
						is_detected = True
						break
				if is_detected:
					output_file.write(word.encode('utf-8') + "\t" + ner_tag + "\n")		
					continue						
			if not is_detected:
				if is_debugging:
					print "%s \t O" % word
				output_file.write(word.encode('utf-8') + "\t" + ner_tag + "\n")
		output_file.close()
	else:
		print "Annotation doesn't exist!"


if __name__ == "__main__":
	import argparse
	
	parser = argparse.ArgumentParser(description='Convert MAT output file into CoNLL format.')
	parser.add_argument('--mat_dir', metavar='dir', dest='mat_dir', help='MAT input directory')
	parser.add_argument('--conll_dir', metavar='dir', dest='conll_dir', help='Conll output directory')
	args = parser.parse_args()	

	# mat_dir = "/home/sunghwan/workspace/ner_project/data/trove/exp_data/dev_50_mat_2/"
	# conll_dir = "/home/sunghwan/workspace/ner_project/data/trove/exp_data/dev_50_conll_2/"

	for mat_file in listdir(args.mat_dir):
		if isfile(join(args.mat_dir,mat_file)):
			# read the output file of MAT annotation tool
			# write CoNLL format for the input of Stanford NER tagger						
			writeConll(args.mat_dir, mat_file, args.conll_dir)

	


