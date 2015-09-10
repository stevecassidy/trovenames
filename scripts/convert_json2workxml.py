#!/usr/bin/python

## convert Json feed data into Work XML files
## Note that convert_jsonlist.sh should be run on the feed data before running this script

import os
import re
import json
from collections import namedtuple
from lxml import etree
from xml.sax.saxutils import unescape

Work = namedtuple("Work", ["id", "source", "title", "date"])
work_link = 'http://trove.nla.gov.au/ndp/del/article/'


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


if __name__ == "__main__":
	import argparse
	
	parser = argparse.ArgumentParser(description='Convert Json feed data into Work XML files.')
	parser.add_argument('--input_file', metavar='file', dest='input_file', help='Json feed data file')
	parser.add_argument('--output_dir', metavar='dir', dest='output_dir', help='XML output directory')
	args = parser.parse_args()
		
	if args.output_dir:
		work_dir = args.output_dir + 'work_xmls/'
		if not os.path.exists(work_dir):
			os.makedirs(work_dir)
	
	buildWorkXML(args.input_file, work_dir)
	
