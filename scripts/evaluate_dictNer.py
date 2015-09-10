#!/usr/bin/python

## read CoNLL format, tags only PERSON using HuNI dictionary
## and finally estimate Precision, Recall and F1 only for PERSON
## in order to investigate the effectiveness of Stanford NER

from __future__ import division	
import io
import sys
import fileinput
import argparse
import collections


huniname_dict = set()

def readHuniNames():
	huniname_file = open("../dict/huni_names_v1.dic", "r")	
	for word in huniname_file.xreadlines():
		word = word.lstrip()
		word = word.rstrip()	
		if word not in huniname_dict:
			huniname_dict.add(word)
	huniname_file.close()
	print 'HuNI dictionary has been loaded (' + str(len(huniname_dict)) + ' names)'

Word_tag = collections.namedtuple("Word_tag", ["word", "manual_tag", "predicted_tag"])

def tagPerson(conll_file):
	
	tag_list = []
	# read CoNLL file
	for line in open(args.conll_file):
		tokens = line.split('\t')
		if len(tokens) == 2:
			word = tokens[0]
			manual_tag = tokens[1].rstrip('\n')

		if word in huniname_dict:
			predicted_tag = 'PERSON'			
		else:
			predicted_tag = 'O'

		tag_list.append(Word_tag(word, manual_tag, predicted_tag))
		
	return tag_list


if __name__ == "__main__":
	
	parser = argparse.ArgumentParser(description='Tag PERSON only using HuNI name dictionary and calculate P, R and F1.')
	parser.add_argument('--conll_file', metavar='file', dest='conll_file', help='conll input file')
	args = parser.parse_args()
	
	readHuniNames()
	
	is_tp = is_fp = is_fn = False
	num_tp = num_fp = num_fn = 0
	tag_list = tagPerson(args.conll_file)	
	for tag_line in tag_list:
#		print tag_line
		
		if (tag_line.manual_tag=='PERSON') & (tag_line.predicted_tag=='PERSON'):
			is_tp = True
		else:
			if is_tp:
				num_tp += 1
				is_tp = False
	
		if ((tag_line.manual_tag=='O')|(tag_line.manual_tag=='LOCATION')|(tag_line.manual_tag=='ORGANIZATION')) & (tag_line.predicted_tag=='PERSON'):
			is_fp = True
		else:
			if is_fp:				
				num_fp += 1
				is_fp = False
				
		if (tag_line.manual_tag=='PERSON') & (tag_line.predicted_tag=='O'):
			is_fn = True
		else:
			if is_fn:
				num_fn += 1
				is_fn = False
				
	
	if is_tp:
		num_tp += 1
	elif is_fp:
		num_fp += 1
	elif is_fn:
		num_fn += 1
			
		
	precision = num_tp / (num_tp + num_fp)
	recall = num_tp / (num_tp + num_fn)
	f1_score = 2 * (precision * recall) / (precision + recall)
			
	print 'P \t R \t F1 \t TP \t FP \t FN'
	print '%f \t %f \t %f \t %d \t %d \t %d' % (precision, recall, f1_score, num_tp, num_fp, num_fn)

