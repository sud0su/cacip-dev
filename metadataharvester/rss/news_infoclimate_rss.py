import sys
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE","geonode.settings")
if __name__ == '__main__':
    import django
    django.setup()

import feedparser
import requests
import datetime
import time

from metadataharvester.utils import create_thumbnail, save_document, BaseHarvester
from geonode.documents.models import News

class Harvester(BaseHarvester):

    feed = 'https://infoclimate.org/category/news/feed/?paged={0}'
    datasource = 'infoclimate.org'
    harvest_choices_keys = ['harvest_all','harvest_latest']

    def harvest_all(self, **kwargs):
        page = 1
        item_num = 0

        while True:
            response = requests.get(self.feed.format(page))
            if response.status_code == 200:
                NewsFeed = feedparser.parse(self.feed.format(page))
                for entry in NewsFeed.entries:
                    docparams = {
                        'title': entry.title,
                        'owner_id': self.harvester_id,
                        'doc_url': entry.links[0].href,
                        'datasource': self.datasource,
                        'doc_type': self.doc_type,
                        'input_method': self.input_method,
                        'date': datetime.datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S +0000').isoformat(),
                        'abstract': entry.summary,
                        'sourcetext': str(entry),
                    }
                    # print(docparams)
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

                    # create_thumbnail(
                    #     doc_url=docparams['doc_url'],
                    #     doc=None,
                    #     external_thumbnail_url=specialparams['external_thumbnail_url']
                    # )
                    # print entry.keys()
                    # print(entry.published)
                    # print(entry.title)
                    # # print(entry.authors)
                    # # print(entry.summary)
                    # print("====================")
                page = page + 1
            else:
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
