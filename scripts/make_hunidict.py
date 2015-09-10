#!/usr/bin/python

## extract person-related properties from Json objects of HuNI names 
## and create a dictionary (v2)

import io, os, re, sys, json
from bs4 import BeautifulSoup

def writeDictionary(huni_file, dict_file):
	tot_name_size = 0
	dic_name_size = 0
	with open(huni_file, "r") as file:
		outfile = open(dict_file,"w")
		data = json.load(file)
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
						
				person_data = {}
				person_data['lastName'] = family_name
				person_data['firstName'] = individual_name
				person_data['occupation'] = occupation
				person_data['biography'] = biography
			
				dic_name_size += 1

				json.dump(person_data,outfile, indent=4)
			
			except KeyError: continue
		outfile.close()
		print 'number of names in the HuNI feed: %d ' % (tot_name_size) 
		print 'number of names in our HuNI dictionary: %d ' % (dic_name_size)


if __name__ == "__main__":
	import argparse
	
	# filepath: '../data/huni_names.json'
	parser = argparse.ArgumentParser(description='Extract person information from HuNI feed and Make a dictionary.')
	parser.add_argument('--huni_file', metavar='file', dest='huni_file', help='huni name input file')
	parser.add_argument('--dict_file', metavar='file', dest='dict_file', help='dictionary output file')
	args = parser.parse_args()
	
	writeDictionary(args.huni_file, args.dict_file)	


