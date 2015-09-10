#!/usr/bin/python

## generate unique id for each person, which is extracted from Json objects of HuNI names 
## and create a person-id mapping dictionary


def uniqid(prefix='', more_entropy=False):
	import string, time, math, random
	
	m = time.time()
	uniqid = '%8x%05x' %(math.floor(m),(m-math.floor(m))*1000000)
	if more_entropy:
		valid_chars = list(set(string.hexdigits.lower()))
		entropy_string = ''
		for i in range(0,10,1):
			entropy_string += random.choice(valid_chars)
		uniqid = uniqid + entropy_string
	return uniqid


if __name__ == "__main__":	
	import io, os, re, sys, json
	import argparse
	import uuid
	from bs4 import BeautifulSoup

	# filepath: '../data/huni_names.json'
	parser = argparse.ArgumentParser(description='Extract person information from HuNI feed and Make a dictionary.')
	parser.add_argument('--huni_file', metavar='file', dest='huni_file', help='huni name input file')
	parser.add_argument('--map_file', metavar='file', dest='map_file', help='person-id output file')
	args = parser.parse_args()

	tot_name_size = 0
	dic_name_size = 0
	with open(args.huni_file, "r") as file:
		outfile = open(args.map_file,"w")
		data = json.load(file)
		person_dict = {}
		for doc in data["response"]["docs"]:
			tot_name_size += 1
			try:
				family_name = doc["familyName"]
				individual_name = doc["individualName"]
				occupation = doc["occupation"]
				biography = doc["biography"]			
			
				family_name = family_name.encode('utf-8').strip()
				individual_name = individual_name.encode('utf-8').strip()
				occupation = occupation.encode('utf-8').strip()
				biography = biography.encode('utf-8').strip()
				biography = biography.replace('\r', ' ').replace('\n', ' ').replace('\t', '').replace('\'', '')
				biography = ' '.join(biography.split())			
			
				person_name = individual_name.lower() + ' ' + family_name.lower()
				person_dict[person_name] = uniqid(person_name)
		
				dic_name_size += 1			
			except KeyError: continue

		json.dump(person_dict, outfile, indent=4)
		outfile.close()
		print 'number of names in the HuNI feed: %d ' % (tot_name_size) 
		print 'number of names in our HuNI name dictionary: %d ' % (dic_name_size)
		print 'number of names in our HuNI name-id dictionary: %d ' % len(person_dict)


