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

url = 'http://stat.kg/en/publications/'
total_added = 0
admin_id = 1000  # admin user id
datasource = 'stat.kg/en/publications/'

def get_records(url):
    http = urllib3.PoolManager()
    r = http.request("GET", url)
    return BeautifulSoup(r.data, 'lxml')

def main(url={}):
    global total_added

    getsoup = get_records(url=url)
    content = getsoup.find('div', {'id': 'content'})
    pages = content.find('div', class_='content')
    pagetitle = pages.find_all('h3')
    listoftitle = [x.text for x in pagetitle]
    gettable = [x for x in pagetitle]

    while (total_added < len(listoftitle)):
        for header in pages.find_all('h3', text=gettable[total_added].text):
            nextNode = header
            while True:
                nextNode = nextNode.nextSibling
                if nextNode is None:
                    break
                if isinstance(nextNode, Tag):
                    if nextNode.name == "h3":
                        break
                    table_body = nextNode.find('tbody')
                    rows = table_body.find_all('tr')
                    for row in rows:
                        for a in row.findAll('a'):
                            try:
                                url = a['href']
                            except Exception as identifier:
                                continue
                            else:
                                doc_url = 'http://stat.kg'+url
                                print("Web Page: ", doc_url)
                                harvest_all(doc_url)
        total_added = total_added + 1
    print("Added", total_added)
    
def harvest_all(url, db=None, **kwargs):
    global total_added

    soup = get_records(url)
    results = soup.find_all("div", class_="content")

    for result in results:
        checktitle = result.find('h1')
        checkthumbnail = result.find('img', class_="img-responsive")
        checkbody = result.find('div', class_="col-md-9").select_one("p:nth-of-type(3)")

        title = None if checktitle == None else checktitle.get_text()
        thumbnail = None if checkthumbnail == None else checkthumbnail["src"]
        body = None if checkbody == None else checkbody.get_text()

        docparams = {
            'title': title,
            'owner_id': admin_id,
            'doc_url': url,
            'datasource': datasource,
            # 'date': postdate,
            'abstract': body,
        }
        
        specialparams = {
            'external_thumbnail_url': 'http://stat.kg'+thumbnail,
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
