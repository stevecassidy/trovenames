#!/usr/bin/python

## generate HuNI feed data in Jason format
## each Jason contains six items
## (article ID, person name, article source, article title, artilce date, text snippet)


from __future__ import division
import os, io, sys, re, string, json, gzip, time, random
from bs4 import BeautifulSoup
import threading, Queue
import ner	# python inteface to Stanford NER server

is_debugging = False
is_queue_counting = True

num_workers = 100000
counting_unit = 100000

num_splits = 5
seed = 10
random.seed(seed)
port_number = 8080
st_remote_ners = {}
for i in xrange(num_splits):	
	st_remote_ners[i] = ner.SocketNER(host='localhost', port=port_number)
	port_number += 10


huniname_dict = set()
completed = object()


def readHuniDict():	
	huni_file = './huni_names_v2.dic'
	infile = open(huni_file)
	json_objects = json.load(infile)
	infile.close()
	
	print 'Huni Dictionary contains ' + str(len(json_objects)) + ' names'
	
	for i in xrange(len(json_objects)):
		try:
			name = json_objects[i]["firstName"] + ' ' + json_objects[i]["lastName"]
			if name not in huniname_dict:
				huniname_dict.add(name.lower())
		except ValueError:
			print "Decoding JSON has failed"


def readData(name, out_queue):
	read_counter = 0
	f = gzip.open(name)
	for json_list in f:
		json_object = json.loads(json_list)
		out_queue.put(json_object)
		
		if is_queue_counting:
			read_counter += 1
			if (read_counter%counting_unit) == 0:
				sys.stdout.write('R(%d)' % counting_unit)			
	out_queue.put(completed)


def splitData(in_queue, out_queues):
	split_counter = 0
	for json_object in iter(in_queue.get, completed):
		n = random.randint(0, num_splits-1)
		out_queues[n].put(json_object)
		
		if is_queue_counting:
			split_counter += 1
			if (split_counter%counting_unit) == 0:
				sys.stdout.write('S(%d)' % counting_unit)
	
	for i in xrange(num_splits):
		out_queues[i].put(completed)


def runRemoteStdNERs(in_queue, out_queue, queue_idx):
	ner_counter = 0
	for json_object in iter(in_queue.get, completed):
		try:
			article_id = json_object['id']
			article_text = json_object['fulltext']
		except ValueError:
			print 'Decoding JSON has failed'			

		if is_queue_counting:
			ner_counter += 1
			if (ner_counter%counting_unit == 0):
				sys.stdout.write('R(%d)_Q%d' % (counting_unit,queue_idx))
						
		if (article_id != None) & (article_text != None):
			article_text = re.sub('[^A-Za-z0-9.,\'-]+', ' ', article_text)
			article_text = BeautifulSoup(article_text).get_text().strip()
			article_text = re.sub(r'[^\x00-\x7F]','', article_text)
			
			json_object['fulltext'] = article_text	
			tagged_entities = st_remote_ners[queue_idx].get_entities(article_text)
			if 'PERSON' in tagged_entities:
				json_object['tagged_entities'] = tagged_entities
				result = json_object
				out_queue.put(result)
	out_queue.put(completed)	


def findContext(name, text):
	name_idx = text.find(name)
	name_context = '...'
	name_context += text[name_idx-30:name_idx]
	name_context += text[name_idx:name_idx+(len(name)+30)]
	name_context += '...'
	
	return name_context
	


def writeNames(in_queue, out_file, queue_idx, st_time):
	write_counter = 0
	with open(out_file, 'w') as outfile:
		for json_object in iter(in_queue.get, completed):
			try:
				article_id = json_object['id']
				article_text = json_object['fulltext']
				
				article_source = json_object['titleName']
				article_source = BeautifulSoup(article_source).get_text().strip()
				article_source = re.sub(r'[^\x00-\x7F]','', article_source)				
				
				article_title = json_object['heading']
				article_title = BeautifulSoup(article_title).get_text().strip()
				article_title = re.sub(r'[^\x00-\x7F]','', article_title)
				
				article_date = json_object['date']
				tagged_entities = json_object['tagged_entities']
				name_list = list(set(tagged_entities['PERSON']))
			except ValueError:
				print 'Decoding JSON has failed'

			if is_queue_counting:
				write_counter += 1
				if (write_counter%counting_unit == 0):
					sys.stdout.write('W(%d)_Q%d' % (counting_unit,queue_idx))
					
			for name in name_list:				
				name = name.strip('-').strip().strip('-')					
				name = name.replace('\\', '')
				name = re.sub('\w*/', '', name)				
				
				if name.lower() in huniname_dict:
					name_context = findContext(name, article_text)
					
					if is_debugging:
						print(article_id + '\t' + name + '\t' + article_source + '\t' + article_title + '\t' + article_date + '\t' + name_context + '\n')
					
					feed_data = {}
					feed_data['article_id'] = article_id
					feed_data['name'] = name
					feed_data['article_source'] = article_source
					feed_data['article_title'] = article_title
					feed_data['article_date'] = article_date
					feed_data['name_context'] = name_context					
					json.dump(feed_data, outfile, indent=4)
					
					
	outfile.close()
	print("running time: %s secs in Queue%d" % (time.time()-st_time, queue_idx))



if __name__ == "__main__":
	import argparse

	parser = argparse.ArgumentParser(description='Generate HuNI feed data.')
	parser.add_argument('--input_file', metavar='file', dest='input_file', help='Trove data file')
	parser.add_argument('--out_file', metavar='file', dest='out_basename', help='HuNI feed file')
	args = parser.parse_args()

	start_time = time.time()

	readHuniDict()

	# read data from trove	
	read_queue = Queue.Queue(num_workers)
	threading.Thread(target=readData, args=(args.input_file, read_queue)).start()
	
	# split data for parallel processing
	split_queues = {}
	for i in xrange(num_splits):
		split_queues[i] = Queue.Queue(num_workers)
	threading.Thread(target=splitData, args=(read_queue, split_queues)).start()

	# run multiple remote Stanford NER on read articles
	stdner_queues = {}
	for i in xrange(num_splits):
		stdner_queues[i] = Queue.Queue()
		threading.Thread(target=runRemoteStdNERs, args=(split_queues[i], stdner_queues[i], i)).start()

	out_ext = ".txt"
	for i in xrange(num_splits):
		output_file = "%s_%s%s" % (args.out_basename, i, out_ext)
		threading.Thread(target=writeNames, args=(stdner_queues[i], output_file, i, start_time)).start()

	sys.exit()	


	
