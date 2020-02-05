'''
for first run call:
    harvest_all()
    create_all_thumbnail()
to update:
    harvest_latest()
    create_all_thumbnail()
api: oai-pmh
api doc: http://www.openarchives.org/OAI/openarchivesprotocol.html#ProtocolMessages
'''

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","geonode.settings")
if __name__ == '__main__':
    import django
    django.setup()

from bs4 import BeautifulSoup
from cStringIO import StringIO
from django.core.files.storage import default_storage as storage
from geonode.base.models import Region
from geonode.documents.models import KnowledgehubDocument
from geonode.documents.renderers import generate_thumbnail_content
from metadataharvester.utils import save_document, delayed_requests, BaseHarvester
from PIL import Image
from sickle import Sickle, oaiexceptions
from tempfile import NamedTemporaryFile

import datetime
import re
import requests
import sys
import time
import urlparse

class Harvester(BaseHarvester):
    
    datezformat = '%Y-%m-%dT%H:%M:%SZ' # date format in UTC Z notation, Z=Zulu means UTC+0
    datasource = 'openknowledge.worldbank.org'
    delay_seconds = 1
    thumb_name_tpl = 'document-{0}-thumb.png'
    harvest_choices_keys = ['harvest_all','harvest_latest']
    harvest_url = 'https://openknowledge.worldbank.org/oai/request'

    def get_records_iterator(self, url=harvest_url, params={}):
        sickle = Sickle(url)
        params.update({'metadataPrefix':'oai_dc','set':'climate_change'})
        records = sickle.ListRecords(**params)
        return records

    def harvest_all(self, params={}):
        '''
        harvest and save all records from oai repository
        '''
        records = self.get_records_iterator(params=params)
        while True:
            try:
                record = records.next()
            except oaiexceptions.NoRecordsMatch as identifier:
                print '%s.%s'%(identifier.__module__, identifier.__repr__())
                print 'endpoint:', records.sickle.endpoint
                print 'params:', records.params
                print 'resumption_token:', records.resumption_token.token
                break
            except StopIteration:
                print 'end of loop'
                break
            handle = record.header.identifier.split(':')[-1]
            # thumbnail_url = 'https://openknowledge.worldbank.org/bitstream/handle/{0}/?sequence=4'.format(handle)
            doc_url = next(i for i in record.metadata['identifier'] if handle in i) or \
                next(i for i in record.metadata['identifier'] if 'http://documents.worldbank.org' in i)
            docparams = {
                'doc_url': doc_url,
                'title': '\n'.join(record.metadata.get('title', [])),
                'owner_id': self.harvester_id,
                # 'papersize':row[8],
                'datasource': self.datasource,
                'doc_type': self.doc_type,
                'input_method': self.input_method,
                # 'subtitle':row[12],
                # 'category_id':row[5],
                'date': record.header.datestamp,
                'abstract': '\n'.join(record.metadata.get('description', [])),
                'sourcetext': record.raw,
            }
            specialparams = {
                'keywords': record.metadata.get('subject', []),
                'creators': record.metadata.get('creator', []),
                # 'thumbnail_url': thumbnail_url,
            }
            self.save_document(docparams, specialparams, basemodel=KnowledgehubDocument)
            # print record.header.identifier, records.resumption_token

    def harvest_from_date(self, datefrom, dateuntil=datetime.datetime.utcnow().strftime(datezformat)):
        '''
        harvest records from datefrom to dateuntil
        '''
        self.harvest_all({'from':datefrom, 'until':dateuntil})

    def harvest_latest(self):
        '''
        update document newer than latest existing document
        '''
        try:
            latest = KnowledgehubDocument.objects.filter(datasource=self.datasource).latest('date')
        except KnowledgehubDocument.DoesNotExist as identifier:
            print 'No latest document found, presumed empty. Switch to harvest_all().'
            self.harvest_all()
        else:
            print 'latest document is:', latest.doc_url
            print 'latest document date is:', latest.date.strftime(self.datezformat)
            self.harvest_from_date(latest.date.strftime(self.datezformat))

# def save_document(docparams, specialparams, insertonly=False, basemodel=Document):
#     '''
#     save or update document
#     '''
#     try:
#         doc = basemodel.objects.get(doc_url=docparams['doc_url'])
#     except basemodel.DoesNotExist:
#         print 'insert new Document:', docparams['doc_url']
#         doc = basemodel(**docparams)
#         mode = 'insert'
#     else:
#         if not insertonly:
#             print 'update existing Document:', docparams['doc_url']
#             for (key, value) in docparams.items():
#                 setattr(doc, key, value)
#         mode = 'update'

#     if (insertonly and mode == 'insert') or not insertonly:
#         doc.save()

#         # create_thumbnail(docparams['doc_url'])

#         if 'keywords' in specialparams:
#             doc.keywords.add(*specialparams['keywords'])

#         if 'creators' in specialparams:
#             doc.creators.add(*specialparams['creators'])

#         if 'regions' in specialparams:
#             regions = Region.objects.filter(name__in=specialparams['regions'])
#             doc.regions.add(*regions)

#         # valid_keywords = filter(None, row[7].split("-"))
#         # doc.keywords.add(*valid_keywords)
#         # row[16] = doc.id
#         # loc = Region.objects.get(pk=row[4])
#         # doc.regions.add(loc)
#     return mode

    def create_all_thumbnail(self):
        '''
        loop all documents and create thumbnail if not exist
        '''
        docs = KnowledgehubDocument.objects.filter(datasource=self.datasource)
        for doc in docs:
            # handle = re.findall('\d+\/\d+', doc.doc_url)[0]
            # thumb_name_tpl.format(doc.uuid)
            file_path = os.path.join('thumbs/', self.thumb_name_tpl.format(doc.uuid))
            if not storage.exists(file_path):
                print 'create thumbnail for:', doc.doc_url
                self.create_thumbnail(doc.doc_url, doc)

    def create_thumbnail(self, doc_url, doc):
        '''
        create document thumbnail
        '''

        # save thumbnail
        html_response = self.delayed_requests({'args':[doc_url], 'kwargs':{'allow_redirects':True}})
        soup = BeautifulSoup(html_response.content, 'html.parser')
        elm_thumbnail = soup.find("img", {"id": "campaign-icon"})
        img_response = self.delayed_requests({'args':[urlparse.urljoin(html_response.url, elm_thumbnail.attrs['src'])], 'kwargs':{'allow_redirects':True}})
        # img_response = requests.get(specialparams['thumbnail_url'], allow_redirects=True)
        if img_response.status_code == 200:
            doc = doc or KnowledgehubDocument.objects.get(doc_url=doc_url)
            doc.save_thumbnail(
                filename = self.thumb_name_tpl.format(doc.uuid),
                image = generate_thumbnail_content(StringIO(img_response.content), size=(600, 450))
            )
        else:
            print 'img_response.status_code:', img_response.status_code
            # print "docparams['thumbnail_url']:", specialparams['thumbnail_url']

# def delayed_requests(requestsparams, module=sys.modules[__name__]):
#     '''
#     request with delay time to work around rate limiter
#     '''
#     if not hasattr(module, 'delay_seconds'):
#         setattr(module, 'delay_seconds', 0)

#     if not hasattr(module, 'session'):
#         setattr(module, 'session', requests.session())

#     while True:
#         if getattr(module, 'delay_seconds'):
#             print 'wait for %s seconds' % module.delay_seconds
#             time.sleep(module.delay_seconds) 
#         response = module.session.get(*requestsparams.get('args',[]), **requestsparams.get('kwargs',{}))
#         if response.status_code == 429: # rate limited
#             module.delay_seconds += 1
#             print '%s.delay_seconds: %s' % (module, module.delay_seconds)
#         else:
#             return response

if __name__ == "__main__":
    harvester = Harvester()
    harvester.dispatch_args()
