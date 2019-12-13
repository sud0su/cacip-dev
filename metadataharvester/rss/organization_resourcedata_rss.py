import sys
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE","geonode.settings")
if __name__ == '__main__':
    import django
    django.setup()
    
import feedparser
import requests
import datetime

from metadataharvester.utils import create_thumbnail, save_document
from geonode.documents.models import KnowledgehubDocument

admin_id = 1000 
feed = 'https://www.resourcedata.org/feeds/organization/rgi.atom?page={0}'
datasource = 'resourcedata.org'
doc_type = 'organisation'

def harvest_all(**kwargs):
    '''
    harvest all document, existing document will be updated.
        
    Parameters
    ----------
    insertonly: bool, optional
        only insert new document
    insertnewonly: bool, optional
        only insert new document, if document already exist then exit
    limit: int, optional
        max number of inserted/updated document
    '''
    item_num = 0
    page = 1
    while True:
        NewsFeed = feedparser.parse(feed.format(page))
        if NewsFeed.entries:
            for entry in NewsFeed.entries:
                docparams = {
                    'title': entry.title,
                    'owner_id': admin_id,
                    'doc_url': entry.link,
                    'doc_type': doc_type,
                    'datasource': datasource,
                    'date': datetime.datetime(*entry.published_parsed[:6]).isoformat(),
                    # 'abstract': entry.summary,
                    'sourcetext': str(entry),
                }

                specialparams = {
                    # 'external_thumbnail_url': file,
                }
                if hasattr(entry,'authors'):
                    specialparams['author'] = [i['name'] for i in entry.authors if i['name']]

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

def harvest_latest():
    harvest_all(insertnewonly=True)

if __name__ == "__main__":
    if sys.argv[1] == "harvest_all":
        harvest_all()
    elif sys.argv[1] == "harvest_latest":
        harvest_latest()
    else:
        print 'options are: harvest_all, harvest_latest'
