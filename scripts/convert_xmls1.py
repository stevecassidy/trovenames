#!/usr/bin/python

## convert text feed data into XML files

import uuid
from collections import namedtuple
from lxml import etree
from xml.sax.saxutils import unescape
from bs4 import BeautifulSoup
import re


Person = namedtuple("Person", ["name", "id", "source", "title", "date", "snippet"])
trove_link = 'http://trove.nla.gov.au/ndp/del/article/'
entity_link = 'http://example.org/troveid/'
localtype_link = 'http://xmlns.com/foaf/0.1/Person'
span_head = '<span>'
span_tail = '</span>'


def emphasiseName(name, text):
	name_idx = text.find(name)
	name_text = text[0:name_idx]
	name_text += span_head
	name_text += text[name_idx:name_idx+len(name)]
	name_text += span_tail
	name_text += text[name_idx+len(name):]
	
	return name_text


def writeXML(person_list, output_dir):	
	unique_id = ''
	prv_name = ""
	for p in person_list:
		if prv_name != p.name.lower():
			if prv_name != "":
				
				cpfdescription_tag = etree.SubElement(top_tag, 'cpfDescription')
				identify_tag = etree.SubElement(cpfdescription_tag, 'identity')				
				etree.SubElement(identify_tag, 'entityId').text = entity_link + unique_id
				etree.SubElement(identify_tag, 'entityType').text = 'person'
				nameentry_tag = etree.SubElement(identify_tag, 'nameEntry')
				etree.SubElement(nameentry_tag, 'part', localType=localtype_link).text = prv_name.title()
				description_tag = etree.SubElement(cpfdescription_tag, 'description').text = ' '
			
				outfile = open(output_dir + prv_name + '.xml', 'w')
				outfile.write(unescape(etree.tostring(top_tag, pretty_print=True)))
				outfile.close()

			top_tag = etree.Element('eac-cpf', xmlns='urn:isbn:1-931666-33-4')
			control_tag = etree.SubElement(top_tag, 'control')			
			recordid_tag = etree.SubElement(control_tag, 'recordId')
			unique_id = str(uuid.uuid4().int)
			recordid_tag.text = 'Trove' + unique_id

			sources_tag = etree.SubElement(control_tag, 'sources')
			trove_href = trove_link + p.id
			NS_MAP = {'href': trove_href}
			source_tag = etree.SubElement(sources_tag, 'source', nsmap=NS_MAP)			
			
			descriptivenote_tag = etree.SubElement(source_tag, 'descriptiveNote')
			p_tag = etree.SubElement(descriptivenote_tag, 'p')
			etree.SubElement(p_tag, 'span', localType='dc:source').text = p.source
			etree.SubElement(p_tag, 'span', localType='dc:title').text = re.sub(r'[^\x00-\x7F]','', p.title)
			etree.SubElement(p_tag, 'span', localType='dc:date').text = p.date
			etree.SubElement(descriptivenote_tag, 'p').text = emphasiseName(p.name, p.snippet)

			prv_name = p.name.lower()
		else:
			sources_tag = etree.SubElement(control_tag, 'sources')
			trove_href = trove_link + p.id
			NS_MAP = {'href': trove_href}
			source_tag = etree.SubElement(sources_tag, 'source', nsmap=NS_MAP)						
			
			descriptivenote_tag = etree.SubElement(source_tag, 'descriptiveNote')
			p_tag = etree.SubElement(descriptivenote_tag, 'p')
			etree.SubElement(p_tag, 'span', localType='dc:source').text = p.source
			etree.SubElement(p_tag, 'span', localType='dc:title').text = re.sub(r'[^\x00-\x7F]','', p.title)
			etree.SubElement(p_tag, 'span', localType='dc:date').text = p.date
			etree.SubElement(descriptivenote_tag, 'p').text = emphasiseName(p.name, p.snippet)
			
			prv_name = p.name.lower()
		
def buildDict(in_file):
	person_list = []
	for line in open(in_file, 'r'):
		tokens = line.split('\t')
		p = Person(tokens[1], tokens[0], tokens[2], tokens[3], tokens[4], tokens[5].rstrip('\n'))
		person_list.append(p)

	person_list = sorted(person_list)
	return person_list



if __name__ == "__main__":
	import argparse
	
	parser = argparse.ArgumentParser(description='Convert text feed data into XML files.')
	parser.add_argument('--input_file', metavar='file', dest='input_file', help='Text feed data file')
	parser.add_argument('--output_dir', metavar='dir', dest='output_dir', help='XML output directory')
	args = parser.parse_args()
		
	# input_file = "./names_10000_0.txt"
	# output_dir = "./xmls_10000/"
	
	person_list = buildDict(args.input_file)
	writeXML(person_list, args.output_dir)
	
	
	
	

	


