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

from geonode.documents.models import Event, KnowledgehubDocument
from sickle import Sickle, oaiexceptions
from tempfile import NamedTemporaryFile
from geonode.documents.renderers import generate_thumbnail_content
from PIL import Image
from cStringIO import StringIO
from bs4 import BeautifulSoup
from django.core.files.storage import default_storage as storage
from metadataharvester.utils import save_document, delayed_requests, create_thumbnail, BaseHarvester
from googletrans import Translator

import datetime
import json
import requests
import re
import time
import urlparse
import sys
import threading
import pychrome
import pytz

class Harvester(BaseHarvester):

    datezformat = '%Y-%m-%dT%H:%M:%SZ' # date format in UTC Z notation, Z=Zulu means UTC+0
    datasource = 'ctc-n.org/technical-assistance/projects'
    delay_seconds = 0
    delay_loop_seconds = 0
    thumb_name_tpl = 'document-{0}-thumb.png'
    index_url_tpl = 'https://www.ctc-n.org/api/projects'
    harvest_choices_keys = ['harvest_all','harvest_latest']
    doc_type = 'projects'
    basemodel = KnowledgehubDocument

    def harvest_all(self, **kwargs):
        offset = 0
        item_num = 0
        item_per_page = 5
        # translator = Translator()
        while True:
            index_page_response = requests.get(self.index_url_tpl.format())
            if index_page_response.status_code == 200:
                rows = json.loads(index_page_response.content)
                for row in rows:
                    docparams = {
                        'doc_url': row['URL'],
                        'title': row['Title'],
                        # 'title': el_h1_title.text,
                        'owner_id': self.harvester_id,
                        # 'papersize':row[8],
                        'datasource': self.datasource,
                        'doc_type': self.doc_type,
                        'input_method': self.input_method,
                        # 'subtitle':row[12],
                        # 'category_id':row[5],
                        'date': None,
                        # 'date': datetime.datetime.utcnow().isoformat(),
                        # 'event_date_start': el_span_datestart.attrs['content'],
                        # 'event_date_end': el_span_dateend.attrs['content'],
                        # 'abstract': el_div_abstract.text,
                        'sourcetext': unicode(row),
                    }
                    specialparams = {
                        # 'keywords': [BeautifulSoup(kw, 'html.parser').text for kw in row['CTCN Keyword Matches']],
                        # 'creators': authors,
                        # 'external_thumbnail_url': urlparse.urljoin(docparams['doc_url'], external_thumbnail_url),
                    }
                    if 'CTCN Keyword Matches' in row:
                        specialparams['keywords'] = [BeautifulSoup(kw, 'html.parser').text for kw in row['CTCN Keyword Matches']]
                    if 'Countries' in row:
                        specialparams['regions'] = row['Countries']

                    try:
                        doc = self.save_document(
                            docparams, 
                            specialparams, 
                            insertonly = kwargs.get('insertonly') or kwargs.get('insertnewonly'),
                            basemodel = self.basemodel
                        )

                        # if insertnewonly and document already exist then return
                        if kwargs.get('insertnewonly') and doc.save_mode == 'update':
                            print 'previous latest document: %s' % doc.doc_url
                            print 'new documents added:', item_num
                            return

                        # create_thumbnail(
                        #     doc_url = docparams['doc_url'], 
                        #     doc = None, 
                        #     external_thumbnail_url = specialparams['external_thumbnail_url']
                        # )
                    except Exception as identifier:
                        if kwargs.get('continue_on_error'):
                            self.delay_loop_seconds += 1
                            print str(identifier)
                            print 'continue next loop because continue_on_error=%s' % kwargs.get('continue_on_error')
                            print 'delay for %s seconds' % self.delay_loop_seconds
                            continue
                        else:
                            raise

                    item_num += 1
                    if kwargs.get('limit') and item_num >= kwargs.get('limit'):
                        return

                offset += item_per_page

            else:
                break

            # 1 loop only
            break

        print 'harvested: %s' % (item_num)

if __name__ == "__main__":
    harvester = Harvester()
    harvester.dispatch_args()
