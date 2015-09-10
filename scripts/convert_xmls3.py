#!/usr/bin/python

## convert json feed data into 3 types of XML files (Person, Work and Link)
## Note that convert_jsonlist.sh should be run on the feed data before running this script

import os
import re
import json
from collections import namedtuple
from lxml import etree
from xml.sax.saxutils import unescape

Work = namedtuple("Work", ["id", "source", "title", "date"])
Link = namedtuple("Link", ["name", "id", "snippet"])

person_link = 'http://example.org/troveid/'
work_link = 'http://trove.nla.gov.au/ndp/del/article/'
span_head = '<span>'
span_tail = '</span>'


def readHuniNameIdDict():
	huni_nameid_dict = {}
	huni_file = "./huni_name-id_v2.dic"
	infile = open(huni_file)
	huni_nameid_dict = json.load(infile)
	infile.close()
	
	print 'Huni Name-ID Dictionary contains ' + str(len(huni_nameid_dict)) + ' names'
	return huni_nameid_dict


def emphasiseName(name, text):
	name_idx = text.find(name)
	name_text = text[0:name_idx]
	name_text += span_head
	name_text += text[name_idx:name_idx+len(name)]
	name_text += span_tail
	name_text += text[name_idx+len(name):]
	
	return name_text


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


def writeWorkXML(work_list, output_dir):
	for work in work_list:		
		work_tag = etree.Element('work')
		id_tag = etree.SubElement(work_tag, 'id')		
		id_tag.text = 'work:' + work.id
		url_tag = etree.SubElement(work_tag, 'url')		
		url_tag.text = work_link + work.id
		source_tag = etree.SubElement(work_tag, 'source')
		source_tag.text = work.source
		title_tag = etree.SubElement(work_tag, 'title')
		title_tag.text = re.sub(r'[^\x00-\x7F]','', work.title)		
		date_tag = etree.SubElement(work_tag, 'date')
		date_tag.text = work.date		
		
		xml_file = 'work-' + work.id
		outfile = open(output_dir + xml_file + '.xml', 'w')
		outfile.write(unescape(etree.tostring(work_tag, pretty_print=True)))
		outfile.close()

def buildWorkXML(in_file, output_dir):
	work_list = []
	
	with open(in_file) as json_file:
		data = json.load(json_file)
	
	for item in data:
		if len(item) != 6:
			continue
		try:
			w = Work(item['article_id'], item['article_source'], item['article_title'], item['article_date'])
		except IndexError:
			print item	
		work_list.append(w)

	work_list = sorted(work_list)
	writeWorkXML(work_list, output_dir)


def writeLinkXML(link_list, output_dir, huni_nameid_dict):
	
	for link in link_list:
		person_id = huni_nameid_dict[link.name.lower()]
		link_tag = etree.Element('link')
		id_tag = etree.SubElement(link_tag, 'id')
		id_tag.text = 'person:' + person_id + ':work:' + link.id
		
		a_tag = etree.SubElement(link_tag, 'a')
		a_id_tag = etree.SubElement(a_tag, 'id')
		a_id_tag.text = 'person:' + person_id
		a_reln_tag = etree.SubElement(a_tag, 'reln-to')
		a_reln_tag.text = 'Mentioned in'
		
		b_tag = etree.SubElement(link_tag, 'b')
		b_id_tag = etree.SubElement(b_tag, 'id')
		b_id_tag.text = 'work:' + link.id
		b_reln_tag = etree.SubElement(b_tag, 'reln-to')
		b_reln_tag.text = 'Mentions'
		
		note_tag = etree.SubElement(link_tag, 'notes')
		p_tag = etree.SubElement(note_tag, 'p')
		p_tag.text = emphasiseName(link.name, link.snippet)
			
		xml_file = 'link-person-' + person_id + '-work-' + link.id
		outfile = open(output_dir + xml_file + '.xml', 'w')
		outfile.write(unescape(etree.tostring(link_tag, pretty_print=True)))
		outfile.close()



def buildLinkXML(in_file, output_dir, huni_nameid_dict):
	link_list = []
	
	with open(in_file) as json_file:
		data = json.load(json_file)
	
	for item in data:
		if len(item) != 6:
			continue
		try:
			l = Link(item['name'], item['article_id'], item['name_context'].rstrip('\n'))
		except IndexError:
			print item	
		link_list.append(l)	

	link_list = sorted(link_list)
	writeLinkXML(link_list, output_dir, huni_nameid_dict)



if __name__ == "__main__":
	import argparse
	
	parser = argparse.ArgumentParser(description='Convert Json feed data into 3 types of XML files.')
	parser.add_argument('--input_file', metavar='file', dest='input_file', help='Json feed data file')
	parser.add_argument('--output_dir', metavar='dir', dest='output_dir', help='XML output directory')
	args = parser.parse_args()
	
	huni_nameid_dict = readHuniNameIdDict()
	
	if args.output_dir:
		person_dir = args.output_dir + 'person/'
		work_dir = args.output_dir + 'work/'
		link_dir = args.output_dir + 'link/'				
		
		if not os.path.exists(person_dir):
			os.makedirs(person_dir)
			
		if not os.path.exists(work_dir):
			os.makedirs(work_dir)
			
		if not os.path.exists(link_dir):
			os.makedirs(link_dir)
	
	buildPersonXML(args.input_file, person_dir, huni_nameid_dict)
	
	buildWorkXML(args.input_file, work_dir)
	
	buildLinkXML(args.input_file, link_dir, huni_nameid_dict)
	
