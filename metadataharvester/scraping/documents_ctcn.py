import os
import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geonode.settings")
if __name__ == '__main__':
    import django
    django.setup()

import urllib3
from bs4 import BeautifulSoup
import datetime

from geonode.harvester.utils import create_thumbnail, save_document

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = 'https://www.ctc-n.org/type-resource/document'
total_added = 0
harvester_id = 1000  # admin user id
datasource = 'ctc-n.org/type-resource/document'

def get_records(url):
    http = urllib3.PoolManager()
    r = http.request("GET", url)
    return BeautifulSoup(r.data, 'lxml')

def main(url={}):
    global total_added

    getsoup = get_records(url=url)
    pages = getsoup.find("li", class_='pager-last last').a['href']
    # total = pages.split('=')[1]
    total = 10

    while (total_added < int(total)):
        url = 'https://www.ctc-n.org/type-resource/document?page='+str(total_added)
        print("Web Page: ", url)
        total_added = total_added + 1

        getpost = get_records(url=url)
        content = getpost.find('section', {"id":"block-system-main"})
        posts = content.find('div', class_="inner").find_all('div', class_='node node-resource node-teaser clearfix')
        
        for post in posts:
            geturl = post.find('h2', class_="teaser-title").a['href']
            posturl = 'https://www.ctc-n.org'+geturl
            
            image = post.find("div", class_="field-name-field-document")
            checkimage = None if image == None else image.find(
                'div', class_="field-item even").find('img', class_="pdfpreview-file")
            getimage = None if checkimage == None else checkimage["src"]
            pdf = post.find("div", class_="field-name-field-document").find('div', class_="field-item even").find('span', class_="file")

            if checkimage == None:
                if pdf is not None:
                    getpdfurl = pdf.a['href']
                    getfileicon = pdf.find('img', class_="file-icon")["src"]
            else:
                getfileicon = getimage
                getpdfurl = None
            print("Web Post: ", posturl)
            harvest_all(posturl, getfileicon)

    print("Added ", total_added)

def harvest_all(url, file, db=None, **kwargs):
    global total_added

    soup = get_records(url)
    results = soup.find_all("div", class_="subcontainer")

    for result in results:
        title = result.find('h1', class_="page-header").text

        content = result.find('section', {"id":"block-system-main"}).find('div', class_="inner").find('div', class_="node node-resource clearfix").find('div', class_="content")
        postdate = content.find("div", class_="field-name-field-publication-date")
        body = content.find("div", class_="field-name-body")

        getpostdate = None if postdate == None else postdate.find('div', class_="field-item even").span['content']
        getbody = None if body == None else body.find('div', property="content:encoded").text
        
        docparams = {
            'title': title,
            'owner_id': harvester_id,
            'doc_url': url,
            'datasource': datasource,
            'date': getpostdate,
            'abstract': getbody,
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

    return soup

if __name__ == "__main__":
    main(url)
    # pass
