#!/usr/bin/python

## extract random artilces from a whole Trove data

from __future__ import division
import os, io, re, sys, time
import string, json, gzip
import nltk, random
from bs4 import BeautifulSoup
from nltk import tokenize
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
import aspell, hunspell
import threading, Queue

tot_num_articles = 60000	# total number of articles to be obtained
skip_param = 30000			# maximum value of random selection range

is_debugging = False

aspell_dict = aspell.Speller('lang', 'en')
hunspell_au_dict = hunspell.HunSpell('/usr/share/hunspell/en_AU.dic', '/usr/share/hunspell/en_AU.aff')
ausname_dict = set()


def addAusLexicons():
	# add austraian words into Hunspell dict
	aulexicon_file = open("../dict/aus_lexicon.dic", "r")
	for word in aulexicon_file.xreadlines():
		word = word.lstrip()
		word = word.rstrip()	
		if not hunspell_au_dict.spell(word):
			hunspell_au_dict.add(word)
	aulexicon_file.close()
	# add austraian names into Hunspell dict
	huname_file = open("../dict/huni_names.dic", "r")
	for word in huname_file.xreadlines():
		word = word.lstrip()
		word = word.rstrip()	
		if not hunspell_au_dict.spell(word):
			hunspell_au_dict.add(word)
	huname_file.close()

def readHuniNames():
	huname_file = open("../dict/huni_names.dic", "r")	
	i = 0
	for word in huname_file.xreadlines():
		i += 1
		word = word.lstrip()
		word = word.rstrip()	
		if word not in ausname_dict:
			ausname_dict.add(word)
	huname_file.close()

def preprocess(sentence):
	sentence = re.sub("[^\w]", " ", sentence)
	sentence = sentence.lower()
	sentence = re.sub("\s+", " ", sentence)
	sentence = sentence.lstrip()
	sentence = sentence.rstrip()
	return sentence


def validateArticle(text_id, text):
	threshold_wr = 0.9	# threshold of word ratio
	threshold_tot = 0	# threshold of total number of words in an article
	threshold_exist = 5	# threshold of number of existing names for dictionaries
	
	num_exist_names = 0
	num_total_words = 0

	num_exist_words = 0
	num_non_words = 0	
	
	text = BeautifulSoup(text).get_text().strip()
	text = re.sub(r'[^\x00-\x7F]','', text)	
	
	sentences = sent_tokenize(text)
	for sentence in sentences:
		sentence = preprocess(sentence)
		words = nltk.word_tokenize(sentence)
		for word in words:
			if aspell_dict.check(word) | hunspell_au_dict.spell(word):
				num_exist_words += 1
			else:
				num_non_words += 1
			if word in ausname_dict:
				num_exist_names += 1
	num_total_words = num_exist_words + num_non_words
	if num_total_words == 0:
		print ('denominator is zero! in ' + text_id)
		return False
	word_ratio = num_exist_words/num_total_words
	if is_debugging:
		print ("#Existing words: " + str(num_exist_words) + ", #Non-existing words: " + str(num_non_words))
		print ("Word Ratio: %0.2f" % word_ratio)
	if (num_total_words > threshold_tot) & (num_exist_names > threshold_exist) & (word_ratio>=threshold_wr):
		return True
	else:
		return False


completed = object()

def processData(in_queue, out_queue):
	sel_num_articles = 0
	for json_object in iter(in_queue.get, completed):
		try:
			article_id = json_object['id']
			article_text = json_object['fulltext']
			if (article_id != None) & (article_text != None):
				is_statisfied = validateArticle(article_id, article_text)
				if is_statisfied:
					sel_num_articles += 1
					result = json_object
					out_queue.put(result)					
		except ValueError:
			print 'Decoding JSON has failed'

	out_queue.put(completed)
	print ("Total number of articles: " + str(tot_num_articles))
	print ("Selected number of articles: " + str(sel_num_articles))



def readData(name, queue):
	i = 1
	j = 1
	num_skips = random.randrange(1,skip_param)
	f = gzip.open(name)
	for json_list in f:		
		if j < num_skips:
			j += 1
			json_object = json.loads(json_list)			
			continue
		
		json_object = json.loads(json_list)
		if i > tot_num_articles:
			break
		i += 1
		queue.put(json_object)
		j = 1
		num_skips = random.randrange(1,skip_param)				
	queue.put(completed)



def writeOut(name, queue):
	with io.open(name, 'w', encoding='utf-8') as outfile:
		for json_object in iter(queue.get, completed):
			outfile.write(unicode(json.dumps(json_object, indent=4, ensure_ascii=False)))
	outfile.close()	
	

def printOut(queue):
	for json_object in iter(queue.get, completed):
		print "***************************************"
		print json_object
		print "***************************************"		




if __name__ == "__main__":
	import argparse
	
	parser = argparse.ArgumentParser(description='Generate Trove sample data.')
	parser.add_argument('--input_file', metavar='file', dest='input_file', help='Trove data file')
	parser.add_argument('--output_file', metavar='file', dest='output_file', help='Trove sample data file')
	args = parser.parse_args()

	# input_file = "../data/trove/data.gz"
	# output_file = "../data/trove/data_0.9_5.json"

	# use additinoal Australian lexicons
	addAusLexicons()

	readHuniNames()

	start_time = time.time()
	
	in_queue = Queue.Queue()
	out_queue = Queue.Queue()

	threading.Thread(target=readData, args=(args.input_file, in_queue)).start()
	threading.Thread(target=processData, args=(in_queue, out_queue)).start()

	writeOut(args.output_file, out_queue)
	
	if is_debugging:
		printOut(out_queue)	

	print("running time: %s secs" % (time.time() - start_time))
	sys.exit()


