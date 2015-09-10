#!/usr/bin/python

## convert Json feed data into Person XML files
## Note that convert_jsonlist.sh should be run on the feed data before running this script

import os
import re
import json
from lxml import etree
from xml.sax.saxutils import unescape

person_link = 'http://example.org/troveid/'

def readHuniNameIdDict():
	huni_nameid_dict = {}
	huni_file = "./huni_name-id_v2.dic"
	infile = open(huni_file)
	huni_nameid_dict = json.load(infile)
	infile.close()
	return huni_nameid_dict


def writePersonXML(person_names, output_dir, huni_nameid_dict):
	for person_name in person_names:
		person_id = huni_nameid_dict[person_name.lower()]
		person_tag = etree.Element('person')
		id_tag = etree.SubElement(person_tag, 'id')
		id_tag.text = 'person:' + person_id
		url_tag = etree.SubElement(person_tag, 'url')
		url_tag.text = person_link + person_id
		name_tag = etree.SubElement(person_tag, 'name')
		name_tag.text = person_name
		
		xml_file = 'person-' + person_id		
		outfile = open(output_dir + xml_file + '.xml', 'w')
		outfile.write(unescape(etree.tostring(person_tag, pretty_print=True)))
		outfile.close()

def buildPersonXML(in_file, output_dir, huni_nameid_dict):
	person_names = set()
	
	with open(in_file) as json_file:
		data = json.load(json_file)
	
	for item in data:
		if len(item) != 6:
			continue
		try:
			person_names.add(item['name'])
		except IndexError:
			print item		
		
	writePersonXML(person_names, output_dir, huni_nameid_dict)


if __name__ == "__main__":
	import argparse
	
	parser = argparse.ArgumentParser(description='Convert Json feed data into Person XML files.')
	parser.add_argument('--input_file', metavar='file', dest='input_file', help='Json feed data file')
	parser.add_argument('--output_dir', metavar='dir', dest='output_dir', help='XML output directory')
	args = parser.parse_args()
		
	huni_nameid_dict = readHuniNameIdDict()
	
	if args.output_dir:
		person_dir = args.output_dir + 'person_xmls/'
		if not os.path.exists(person_dir):
			os.makedirs(person_dir)
	
	buildPersonXML(args.input_file, person_dir, huni_nameid_dict)
	
