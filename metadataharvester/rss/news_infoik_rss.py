import sys
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE","geonode.settings")
if __name__ == '__main__':
    import django
    django.setup()
    
import requests
import feedparser
import datetime

from bs4 import BeautifulSoup
from metadataharvester.utils import create_thumbnail, save_document, BaseHarvester
from geonode.documents.models import News

class Harvester(BaseHarvester):

    item_num = 0
    offset = 0
    limit = 10
    feed = 'http://infoik.net.kg/?limit={0}&start={1}&format=feed&type=rss'
    datasource = 'infoik.net.kg'
    harvest_choices_keys = ['harvest_all','harvest_latest']

    def harvest_all(self, **kwargs):
        while True:
            NewsFeed = feedparser.parse(self.feed.format(self.limit, self.offset))
            if NewsFeed.entries:
                for entry in NewsFeed.entries:
                    soup_summary = BeautifulSoup(entry.summary, 'html.parser')
                    docparams = {
                        'title': entry.title,
                        'owner_id': self.harvester_id,
                        'doc_url': entry.link,
                        'datasource': self.datasource,
                        'doc_type': self.doc_type,
                        'input_method': self.input_method,
                        'date': datetime.datetime(*entry.published_parsed[:6]).isoformat(),
                        'abstract': soup_summary.text,
                        'sourcetext': str(entry),
                    }

                    specialparams = {
                        'keywords': [i['term'] for i in getattr(entry, 'tags', [])],
                        # 'creators': [entry.author],
                        # 'external_thumbnail_url': file,
                    }
                    if hasattr(entry,'authors'):
                        specialparams['author'] = [i['name'] for i in getattr(entry, 'authors', [])  if i['name']]

                    doc = self.save_document(
                        docparams, 
                        specialparams, 
                        insertonly=kwargs.get('insertonly') or kwargs.get('insertnewonly'), 
                        basemodel=News
                    )

                    el_img = soup_summary.find('img')
                    if el_img:
                        specialparams['external_thumbnail_url'] = el_img.attrs['src']
                        create_thumbnail(
                            doc_url=docparams['doc_url'],
                            doc=None,
                            external_thumbnail_url=specialparams['external_thumbnail_url']
                        )

                    # if insertnewonly and document already exist then return
                    if kwargs.get('insertnewonly') and doc.save_mode == 'update':
                        print 'previous latest document: %s' % doc.doc_url
                        print 'new documents added:', self.item_num
                        return

                    # create_thumbnail(
                    #     doc_url=docparams['doc_url'],
                    #     doc=None,
                    #     external_thumbnail_url=specialparams['external_thumbnail_url']
                    # )

                    self.item_num += 1
                    if kwargs.get('limit') and self.item_num >= kwargs.get('limit'):
                        return

                    # print(docparams)
                self.offset += self.limit
            else:
                print('last page')
                break
            
        print("Added ", self.item_num)

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
