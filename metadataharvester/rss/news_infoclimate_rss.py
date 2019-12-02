import sys
import feedparser
import requests

total_added = 0
admin_id = 1000 
feed = 'https://infoclimate.org/category/news/feed/?paged={0}'
datasource = 'infoclimate.org'


def harvest_all(**kwargs):
    global total_added
    while True:
        response = requests.get(feed.format(total_added))
        if response.status_code == 200:
            NewsFeed = feedparser.parse(feed.format(total_added))
            for entry in NewsFeed.entries:
                docparams = {
                    'title': entry.title,
                    'owner_id': admin_id,
                    'doc_url': entry.links,
                    'datasource': datasource,
                    'date': entry.published,
                    'abstract': entry.summary,
                }
                print(docparams)
                # specialparams = {
                #     'external_thumbnail_url': file,
                # }

                # save_mode = save_document(docparams, specialparams, insertonly=kwargs.get('insertonly') or kwargs.get('insertnewonly'))

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
            total_added = total_added + 1
        else:
            break

    print("Added ", total_added)

if __name__ == "__main__":
    # # harvest_all()
    # # update_latest()
    pass