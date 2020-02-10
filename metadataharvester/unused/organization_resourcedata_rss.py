'''
duplicate result with metadataharvester/api/documents_resourcedataorg_ckan.py
'''

import sys
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE","geonode.settings")
if __name__ == '__main__':
    import django
    django.setup()
    
import feedparser
import requests
import datetime
import json

from metadataharvester.utils import create_thumbnail, save_document, BaseHarvester
from geonode.documents.models import KnowledgehubDocument
from geonode.utils import JSONEncoderCustom

class Harvester(BaseHarvester):

    feed = 'https://www.resourcedata.org/feeds/organization/rgi.atom?page={0}'
    datasource = 'resourcedata.org/organization'
    doc_type = 'organisation'
    harvest_choices_keys = ['harvest_all','harvest_latest']

    def harvest_all(self, **kwargs):
        item_num = 0
        page = 1
        while True:
            NewsFeed = feedparser.parse(self.feed.format(page))
            if NewsFeed.entries:
                for entry in NewsFeed.entries:
                    docparams = {
                        'title': entry.title,
                        'owner_id': self.harvester_id,
                        'doc_url': entry.link,
                        'doc_type': self.doc_type,
                        'datasource': self.datasource,
                        'doc_type': self.doc_type,
                        'input_method': self.input_method,
                        'date': datetime.datetime(*entry.published_parsed[:6]).isoformat(),
                        # 'abstract': entry.summary,
                        'sourcetext': json.dumps(entry, cls=JSONEncoderCustom),
                    }
                    
                    # clean up '\x00' char
                    for i in docparams:
                        if type(docparams[i]) in (str, unicode):
                            docparams[i] = docparams[i].replace('\x00', '')

                    specialparams = {
                        # 'external_thumbnail_url': file,
                    }
                    if hasattr(entry,'authors'):
                        specialparams['author'] = [i['name'] for i in entry.authors if i['name']]

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

                    # create_thumbnail(
                    #     doc_url=docparams['doc_url'],
                    #     doc=None,
                    #     external_thumbnail_url=specialparams['external_thumbnail_url']
                    # )

                    item_num += 1
                    if kwargs.get('limit') and item_num >= kwargs.get('limit'):
                        return
                    # print(docparams)
                page += 1
            else:
                print('last page')
                break

        print("Added ", item_num)

# def harvest_latest():
#     harvest_all(insertnewonly=True)

# if __name__ == "__main__":
#     if sys.argv[1] == "harvest_all":
#         harvest_all()
#     elif sys.argv[1] == "harvest_latest":
#         harvest_latest()
#     else:
#         print 'options are: harvest_all, harvest_latest'

if __name__ == "__main__":
    harvester = Harvester()
    harvester.dispatch_args()
