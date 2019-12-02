import os
import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geonode.settings")
if __name__ == '__main__':
    import django
    django.setup()

import urllib3
from bs4 import BeautifulSoup, Tag
import datetime

from geonode.harvester.utils import create_thumbnail, save_document

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = 'https://cgspace.cgiar.org/discover'
total_added = 0
admin_id = 1000  # admin user id
datasource = 'cgspace.cgiar.org/discover'

def get_records(url):
    http = urllib3.PoolManager()
    r = http.request("GET", url)
    return BeautifulSoup(r.data, 'lxml')

def main(url={}):
    global total_added

    getsoup = get_records(url=url)

    # pages = getsoup.find("li", class_='last-page-link').a.text
    pages = 10

    while (total_added < int(pages)):
        print("Web Page: ", url)
        total_added = total_added + 1
        url = 'https://cgspace.cgiar.org/discover?rpp=10&etal=0&group_by=none&page='+str(total_added)

        getpost = get_records(url=url)
        content = getpost.find('div', {'id': 'aspect_discovery_SimpleSearch_div_search-results'})
        posts = content.find_all('div', class_='row ds-artifact-item')
        
        for post in posts:
            try:
                geturl = post.find('a')['href']
                posturl = 'https://cgspace.cgiar.org'+geturl
            except Exception as identifier:
                continue
            else:
                print("Web Post: ", posturl)
                harvest_all(posturl)

    print("Added", total_added)
    
def harvest_all(url, db=None, **kwargs):
    global total_added
    soup = get_records(url)

    results = soup.find_all('div', class_='item-summary-view-metadata')
    
    for result in results:
        checktitle = result.find('h2', class_="page-header first-page-header").text
        checkabstract = result.find('div', class_="simple-item-view-description item-page-field-wrapper table").find('div').text
        checkthumbUrl = result.find('div', class_="thumbnail").find('img')["src"]

        title = None if checktitle == None else checktitle
        abstract = None if checkabstract == None else checkabstract
        thumbUrl = None if checkthumbUrl == None else 'https://cgspace.cgiar.org'+checkthumbUrl
            
        docparams = {
            'title': title,
            'owner_id': admin_id,
            'doc_url': url,
            'datasource': datasource,
            # 'date': postdate,
            'abstract': abstract,
        }
        specialparams = {
            'external_thumbnail_url': thumbUrl,
        }
        save_mode = save_document(docparams, specialparams, insertonly=kwargs.get('insertonly') or kwargs.get('insertnewonly'))

        create_thumbnail(
            doc_url=docparams['doc_url'],
            doc=None,
            external_thumbnail_url=specialparams['external_thumbnail_url']
        )
            
if __name__ == "__main__":
    main(url)
    pass
