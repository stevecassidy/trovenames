#!/usr/bin/python

## convert Json feed data into Link XML files
## Note that convert_jsonlist.sh should be run on the feed data before running this script

import os
import re
import json
from collections import namedtuple
from lxml import etree
from xml.sax.saxutils import unescape

Link = namedtuple("Link", ["name", "id", "snippet"])
span_head = '<span>'
span_tail = '</span>'


def readHuniNameIdDict():
	huni_nameid_dict = {}
	huni_file = "./huni_name-id_v2.dic"
	infile = open(huni_file)
	huni_nameid_dict = json.load(infile)
	infile.close()
	return huni_nameid_dict


def emphasiseName(name, text):
	name_idx = text.find(name)
	name_text = text[0:name_idx]
	name_text += span_head
	name_text += text[name_idx:name_idx+len(name)]
	name_text += span_tail
	name_text += text[name_idx+len(name):]
	
	return name_text


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
	
	parser = argparse.ArgumentParser(description='Convert Json feed data into Link XML files.')
	parser.add_argument('--input_file', metavar='file', dest='input_file', help='Json feed data file')
	parser.add_argument('--output_dir', metavar='dir', dest='output_dir', help='XML output directory')
	args = parser.parse_args()
		
	huni_nameid_dict = readHuniNameIdDict()
	
	if args.output_dir:
		link_dir = args.output_dir + 'link_xmls/'				
		if not os.path.exists(link_dir):
			os.makedirs(link_dir)
	
	buildLinkXML(args.input_file, link_dir, huni_nameid_dict)
	
