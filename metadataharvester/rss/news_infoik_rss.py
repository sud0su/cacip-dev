import requests
import feedparser

total_added = 0
startpage = 8
admin_id = 1000 
feed = 'http://infoik.net.kg/?limit=8&start={0}&format=feed&type=rss'
datasource = 'infoik.net.kg'

def harvest_all(**kwargs):
    global total_added, startpage
    while True:
        NewsFeed = feedparser.parse(feed.format(startpage))
        if NewsFeed.entries:
            for entry in NewsFeed.entries:
                docparams = {
                    'title': entry.title,
                    # 'owner_id': admin_id,
                    'doc_url': entry.links,
                    # 'datasource': datasource,
                    # 'date': entry.published,
                    # 'abstract': entry.summary,
                }

                specialparams = {
                    'external_thumbnail_url': file,
                }

                save_mode = save_document(docparams, specialparams, insertonly=kwargs.get('insertonly') or kwargs.get('insertnewonly'))

                create_thumbnail(
                    doc_url=docparams['doc_url'],
                    doc=None,
                    external_thumbnail_url=specialparams['external_thumbnail_url']
                )

                total_added = total_added + 1
                # print(docparams)
            startpage = startpage + 8
        else:
            print('last page')
            break
        
    print("Added ", total_added)

if __name__ == "__main__":
    harvest_all()
    # # update_latest()
    # pass