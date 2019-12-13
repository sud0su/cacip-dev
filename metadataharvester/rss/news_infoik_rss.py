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
from metadataharvester.utils import create_thumbnail, save_document
from geonode.documents.models import News

item_num = 0
offset = 0
limit = 10
admin_id = 1000 
feed = 'http://infoik.net.kg/?limit={0}&start={1}&format=feed&type=rss'
datasource = 'infoik.net.kg'

def harvest_all(**kwargs):
    global item_num, offset
    while True:
        NewsFeed = feedparser.parse(feed.format(limit, offset))
        if NewsFeed.entries:
            for entry in NewsFeed.entries:
                soup_summary = BeautifulSoup(entry.summary, 'html.parser')
                docparams = {
                    'title': entry.title,
                    'owner_id': admin_id,
                    'doc_url': entry.link,
                    'datasource': datasource,
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

                doc = save_document(
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
            offset += limit
        else:
            print('last page')
            break
        
    print("Added ", item_num)

def harvest_latest():
    harvest_all(insertnewonly=True)

if __name__ == "__main__":
    if sys.argv[1] == "harvest_all":
        harvest_all()
    elif sys.argv[1] == "harvest_latest":
        harvest_latest()
    else:
        print 'options are: harvest_all, harvest_latest'
