'''
for first run call:
    harvest_all()
to update:
    harvest_latest()
api: ckan
doc: https://docs.ckan.org/en/2.8/api/
'''

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geonode.settings")
if __name__ == '__main__':
    import django
    django.setup()

from geonode.documents.models import Document, KnowledgehubDocument
from sickle import Sickle, oaiexceptions
from tempfile import NamedTemporaryFile
from geonode.documents.renderers import generate_thumbnail_content
from PIL import Image
from cStringIO import StringIO
from bs4 import BeautifulSoup
from django.core.files.storage import default_storage as storage
from metadataharvester.utils import save_document, delayed_requests, BaseHarvester
from googletrans import Translator
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

import datetime
import json
import pychrome
import pytz
import re
import requests
import sys
import threading
import time
import urlparse

datezformat = '%Y-%m-%dT%H:%M:%SZ' # date format in UTC Z notation, Z=Zulu means UTC+0
harvester_id = 1000 # admin user id
datasource = 'resourcedata.org'
delay_seconds = 0
thumb_name_tpl = 'document-{0}-thumb.png'
# index_url_tpl = 'https://www.resourcedata.org/api/3/action/package_search?facet.field=[%22document_type%22]&start=10000&rows=1&sort=metadata_created%20asc' # group by document_type
index_url_tpl = 'https://www.resourcedata.org/api/3/action/package_search?q=type:{2}&start={0}&rows={1}&sort=metadata_created%20desc'
detail_url_tpl = 'https://www.resourcedata.org/api/3/action/package_show?id={0}'
doc_url_tpl = 'https://www.resourcedata.org/{0}/{1}'
timeout = 20 # seconds

def harvest_all(**kwargs):
    offset = 0
    item_num = 0
    item_per_page = 10
    resource_type = 'document'
    doc_type = 'publications'
    # translator = Translator()

    source_ids = []
    if kwargs.get('insertonly') or kwargs.get('insertnewonly'):
        source_ids = [i['source_id'] for i in KnowledgehubDocument.objects.filter(datasource=datasource).values('source_id')]

    while True:
        try:
            print 'index url: %s' % (index_url_tpl.format(offset, item_per_page, resource_type))
            index_page_response = requests.get(index_url_tpl.format(offset, item_per_page, resource_type), timeout=timeout)
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as identifier:
            print identifier
            offset += item_per_page
            continue

        result = json.loads(index_page_response.content)['result']

        if index_page_response.status_code == 200 and result['results']:
            # soup = BeautifulSoup(index_page_response.content, 'html.parser')
            for detail in result['results']:

                # if kwargs.get('insertonly') or kwargs.get('insertnewonly'):
                #     if detail['id'] in source_ids:
                #         continue

                docparams = {
                    'doc_url': doc_url_tpl.format(detail['type'], detail['id']),
                    'title': detail['title'],
                    'owner_id': harvester_id,
                    # 'papersize':row[8],
                    'datasource': datasource,
                    'doc_type': self.doc_type,
                    # 'subtitle':row[12],
                    # 'category_id':row[5],
                    'date': detail['metadata_created'],
                    'abstract': detail['notes'],
                    'source_id': detail['id'],
                    'sourcetext': json.dumps(detail),
                }
                specialparams = {
                    'regions': detail['country'],
                    # 'keywords': record.metadata.get('subject', []),
                    # 'creators': [detail['author']],
                    # 'external_thumbnail_url': urlparse.urljoin(docparams['doc_url'], external_thumbnail_url),
                }
                if detail.get('document_type'):
                    docparams['doc_type'] = detail['document_type']
                if detail.get('tags'):
                    specialparams['tags'] = [i['display_name'] for i in detail['tags'] if i.get('display_name')]
                if detail.get('author'):
                    specialparams['author'] = [detail['author']]
                doc = save_document(
                    docparams, 
                    specialparams, 
                    insertonly=kwargs.get('insertonly') or kwargs.get('insertnewonly'),
                    basemodel=KnowledgehubDocument
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

                item_num += 1
                if kwargs.get('limit') and item_num >= kwargs.get('limit'):
                    return
                    
            offset += item_per_page

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

def harvest_new():
    harvest_all(insertonly=True)

def pychrome_get(url):
    browser = pychrome.Browser()
    tab = browser.new_tab()
    eh = EventHandler(browser, tab)

    tab.start()

    tab.Page.stopLoading()
    tab.Page.enable()
    tab.url = url
    resp = eh.loadurl(url=url)
    # tab.Page.navigate(url=url)
    if resp.get('isloaded'):
        # read dom here
        pass
    return tab

    # tab.stop()
    # browser.close_tab(tab.id)

class EventHandler(object):
    pdf_lock = threading.Lock()

    def __init__(self, browser, tab, timeout = 60):
        self.browser = browser
        self.tab = tab
        self.timeout = timeout
        self.start_frame = None
        self.isloaded = True

        # attach event handler
        tab.Page.frameStartedLoading = self.frame_started_loading
        tab.Page.frameStoppedLoading = self.frame_stopped_loading

    def loadurl(self, url):
        self.tab.Page.navigate(url=url)
        start = time.time()
        while not self.isloaded :
            if time.time() - start > self.timeout:
                return {'istimeout': True}
            time.sleep(1)
        return {'isloaded': True}

    def frame_started_loading(self, frameId):
        self.isloaded = False
        if not self.start_frame:
            self.start_frame = frameId

    def frame_stopped_loading(self, frameId):
        if self.start_frame == frameId:
            self.tab.Page.stopLoading()
            self.isloaded = True

            # with self.pdf_lock:
            #     self.tab.stop()

def parse_date(datestr):
    dateformats = [
        "%A, %d %B %Y %H:%M",
        "%A, %B %d, %Y %H:%M",
    ]
    for dateformat in dateformats:
        try:
            date = datetime.datetime.strptime(datestr, dateformat)
        except ValueError as identifier: # incorrect date format
            continue # just try next format
        else:
            return date

class Harvester(BaseHarvester):

    datezformat = '%Y-%m-%dT%H:%M:%SZ' # date format in UTC Z notation, Z=Zulu means UTC+0
    datasource = 'resourcedata.org'
    delay_seconds = 0
    thumb_name_tpl = 'document-{0}-thumb.png'
    # index_url_tpl = 'https://www.resourcedata.org/api/3/action/package_search?facet.field=[%22document_type%22]&start=10000&rows=1&sort=metadata_created%20asc' # group by document_type
    index_url_tpl = 'https://www.resourcedata.org/api/3/action/package_search?q=type:{2}&start={0}&rows={1}&sort=metadata_created%20desc'
    detail_url_tpl = 'https://www.resourcedata.org/api/3/action/package_show?id={0}'
    doc_url_tpl = 'https://www.resourcedata.org/{0}/{1}'
    timeout = 10 # seconds
    harvest_choices_keys = ['harvest_all','harvest_latest']

    item_per_page = 1000
    resource_type = 'document'
    # translator = Translator()

    def harvest_all(self, **kwargs):

        item_num = 0
        offset = 0
        source_ids = []

        if kwargs.get('insertonly') or kwargs.get('insertnewonly'):
            source_ids = [i['source_id'] for i in KnowledgehubDocument.objects.filter(datasource=datasource).values('source_id')]

        session = self.get_session()
        while True:
            try:
                print 'index url: %s' % (index_url_tpl.format(offset, self.item_per_page, self.resource_type))
                index_page_response = session.get(index_url_tpl.format(offset, self.item_per_page, self.resource_type), timeout=self.timeout)
            except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as identifier:
                print identifier
                offset += self.item_per_page
                continue

            result = json.loads(index_page_response.content)['result']

            if index_page_response.status_code == 200 and result['results']:
                # soup = BeautifulSoup(index_page_response.content, 'html.parser')
                for detail in result['results']:

                    # if kwargs.get('insertonly') or kwargs.get('insertnewonly'):
                    #     if detail['id'] in source_ids:
                    #         continue

                    docparams = {
                        'doc_url': doc_url_tpl.format(detail['type'], detail['id']),
                        'title': detail['title'],
                        'owner_id': self.harvester_id,
                        # 'papersize':row[8],
                        'datasource': self.datasource,
                        'doc_type': self.doc_type,
                        'input_method': self.input_method,
                        # 'subtitle':row[12],
                        # 'category_id':row[5],
                        'date': detail['metadata_created'],
                        'abstract': detail['notes'],
                        'source_id': detail['id'],
                        'sourcetext': json.dumps(detail),
                    }
                    specialparams = {
                        'regions': detail['country'],
                        # 'keywords': record.metadata.get('subject', []),
                        # 'creators': [detail['author']],
                        # 'external_thumbnail_url': urlparse.urljoin(docparams['doc_url'], external_thumbnail_url),
                    }
                    # if detail.get('document_type'):
                    #     docparams['doc_type'] = detail['document_type']
                    if detail.get('tags'):
                        specialparams['tags'] = [i['display_name'] for i in detail['tags'] if i.get('display_name')]
                    if detail.get('author'):
                        specialparams['author'] = [detail['author']]
                    doc = self.save_document(
                        docparams, 
                        specialparams, 
                        insertonly=kwargs.get('insertonly') or kwargs.get('insertnewonly'),
                        basemodel=KnowledgehubDocument
                    )

                    # if insertnewonly and document already exist then return
                    if kwargs.get('insertnewonly') and doc.save_mode == 'update':
                        print 'previous latest document: %s' % doc.doc_url
                        print 'new documents added:', item_num
                        return

                    # self.create_thumbnail(
                    #     doc_url = docparams['doc_url'], 
                    #     doc = None, 
                    #     external_thumbnail_url = specialparams['external_thumbnail_url']
                    # )

                    item_num += 1
                    if kwargs.get('limit') and item_num >= kwargs.get('limit'):
                        return
                        
                offset += self.item_per_page

            else:
                break

if __name__ == "__main__":
    harvester = Harvester()
    harvester.dispatch_args()
