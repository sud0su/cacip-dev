import os
import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geonode.settings")
if __name__ == '__main__':
	import django
	django.setup()

import datetime
import requests
import json

from bs4 import BeautifulSoup
from metadataharvester.utils import create_thumbnail, save_document, BaseHarvester
from geonode.documents.models import News
from HTMLParser import HTMLParser

class Harvester(BaseHarvester):

	url = 'https://www.ctc-n.org/api/news'
	item_num = 0
	datasource = 'ctc-n.org/news'
	parser = HTMLParser()
	harvest_choices_keys = ['harvest_all','harvest_latest']

	# def get_records(url):
	# 	response = requests.get(url)
	# 	data = response.text
	# 	return json.loads(data)

	# def main(url={}):
	# 	global item_num

	# 	news = get_records(url=url)
	# 	test = 1

	# 	while (item_num < int(test)):
	# 		print("Web News: ", news[item_num]['Path'])
	# 		harvest_all(news[item_num]['Path'])
	# 		item_num = item_num + 1

	# 	print("Added", item_num)

	def harvest_all(self, url=url, **kwargs):
		item_num = 0
		index_page_response = requests.get(url)
		# soup = BeautifulSoup(page.text, 'lxml')

		if index_page_response.status_code==200:
			
			for row in json.loads(index_page_response.content):
				# content = soup.find('div', class_="row container-row").find('div', class_="subcontainer")
				# title = content.find('h1', class_="page-header").text

				# section = content.find('main', class_="main_content").find('div', class_="region region-content").find('section', {'id': 'block-system-main'})
				# sectioncontent = section.find('div', class_="inner").find('div', class_="node node-article clearfix").find('div', class_="content")
				
				# date = section.find('div', class_="field-name-field-publication-date").find('div', class_="field-item even").span['content']
				# body = content.find("div", class_="field-name-body").find('div', property="content:encoded").text

				docparams = {
					'title': self.parser.unescape(row['Title']),
					'owner_id': self.harvester_id,
					'doc_url': row['Path'],
					'datasource': self.datasource,
					'doc_type': self.doc_type,
					'input_method': self.input_method,
					'date': datetime.datetime.utcnow().isoformat(),
					# 'abstract': body,
				}
				specialparams = {
					# 'external_thumbnail_url': file,
				}

				doc = self.save_document(
					docparams, 
					specialparams, 
					insertonly=kwargs.get('insertonly') or kwargs.get('insertnewonly'), 
					basemodel=News
				)

				# if insertnewonly and document already exist then return
				if kwargs.get('insertnewonly') and doc.save_mode == 'update':
					print 'previous latest document: %s' % doc.doc_url
					print 'new documents added:', item_num
					return

				# create_thumbnail(
				#     doc_url=docparams['doc_url'],
				#     doc=None,
				#     external_thumbnail_url=specialparams['external_thumbnail_url']
				# )

				item_num += 1
				if kwargs.get('limit') and item_num >= kwargs.get('limit'):
					return

	# return soup

# def harvest_latest():
# 	harvest_all(insertnewonly=True)
			
# if __name__ == "__main__":
# 	if sys.argv[1] == "harvest_all":
# 		harvest_all()
# 	elif sys.argv[1] == "harvest_latest":
# 		harvest_latest()
# 	else:
# 		print 'options are: harvest_all, harvest_latest'

if __name__ == "__main__":
    harvester = Harvester()
    harvester.dispatch_args()
