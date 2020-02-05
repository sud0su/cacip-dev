'''
for first run call:
    harvest_all()
to update:
    harvest_latest()
'''

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","geonode.settings")
if __name__ == '__main__':
    import django
    django.setup()

from geonode.documents.models import Document
from sickle import Sickle, oaiexceptions
from tempfile import NamedTemporaryFile
from geonode.documents.renderers import generate_thumbnail_content
from PIL import Image
from cStringIO import StringIO
from bs4 import BeautifulSoup
from django.core.files.storage import default_storage as storage
from harvester.documents_okrworldbank import save_document, delayed_requests

import datetime
import requests
import re
import time
import urlparse
import sys

datezformat = '%Y-%m-%dT%H:%M:%SZ' # date format in UTC Z notation, Z=Zulu means UTC+0
harvester_id = 1000 # admin user id
datasource = 'infoclimate.org'
delay_seconds = 0
thumb_name_tpl = 'document-{0}-thumb.png'
index_url_tpl = 'https://infoclimate.org/tax/english/enpubl/page/{0}/'

def harvest_all(**kwargs):
    page_num = 1
    item_num = 0
    while True:
        index_page_response = requests.get(index_url_tpl.format(page_num))
        if index_page_response.status_code == 200:
            soup = BeautifulSoup(index_page_response.content, 'html.parser')
            for el in soup.find("div", {"id": "publ"}):
                try:
                    el_a_title = el.select('h2 > a')[0]
                    el_em_authors = el.select('p > em')[0]
                    authors = el_em_authors.text.split(',')
                    publish_year = authors.pop()
                    el_abstract = el.find_next_sibling()
                    el_a_thumbnail = el_abstract.find('a')
                    external_thumbnail_url = el_a_thumbnail.attrs['href'] if el_a_thumbnail else el_abstract.find('img').attrs['src']
                except Exception as identifier:
                    continue
                else:
                    docparams = {
                        'doc_url': el_a_title.attrs['href'],
                        'title': el_a_title.text,
                        'owner_id': harvester_id,
                        # 'papersize':row[8],
                        'datasource': datasource,
                        # 'subtitle':row[12],
                        # 'category_id':row[5],
                        'date': datetime.datetime(int(publish_year), 1, 1).strftime(datezformat),
                        'abstract': el_abstract.text,
                        'sourcetext': unicode(el) + unicode(el_abstract),
                    }
                    specialparams = {
                        # 'keywords': record.metadata.get('subject', []),
                        'creators': authors,
                        'external_thumbnail_url': external_thumbnail_url,
                    }
                    save_mode = save_document(docparams, specialparams, insertonly=kwargs.get('insertonly') or kwargs.get('insertnewonly'))

                    # if insertnewonly and document already exist then return
                    if kwargs.get('insertnewonly') and save_mode == 'update':
                        print 'new documents added:', item_num
                        return

                    create_thumbnail(
                        doc_url = docparams['doc_url'], 
                        doc = None, 
                        external_thumbnail_url = specialparams['external_thumbnail_url']
                    )

                    item_num += 1
                    if kwargs.get('limit') and item_num >= kwargs.get('limit'):
                        return
            page_num += 1
        else:
            break

def create_thumbnail(doc_url, doc, external_thumbnail_url):
    '''
    create document thumbnail
    '''

    img_response = delayed_requests({'args':[external_thumbnail_url], 'kwargs':{'allow_redirects':True}}, module=sys.modules[__name__])
    if img_response.status_code == 200:
        doc = doc or Document.objects.get(doc_url=doc_url)
        doc.save_thumbnail(
            filename = thumb_name_tpl.format(doc.uuid),
            image = generate_thumbnail_content(StringIO(img_response.content), size=(600, 450))
        )
    else:
        print 'img_response.status_code:', img_response.status_code

def harvest_latest():
    harvest_all(insertnewonly=True)

if __name__ == "__main__":
    # harvest_all()
    # harvest_latest()
    pass
