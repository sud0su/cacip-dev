import os
import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geonode.settings")
if __name__ == '__main__':
    import django
    django.setup()

import requests
import json
from bs4 import BeautifulSoup
from geonode.harvester.utils import create_thumbnail, save_document

url = 'https://www.ctc-n.org/api/news'
total_added = 0
admin_id = 1000  # admin user id
datasource = 'ctc-n.org/news'

def get_records(url):
    response = requests.get(url)
    data = response.text
    return json.loads(data)

def main(url={}):
    global total_added

    news = get_records(url=url)
    test = 1

    while (total_added < int(test)):
        print("Web News: ", news[total_added]['Path'])
        harvest_all(news[total_added]['Path'])
        total_added = total_added + 1

    print("Added", total_added)

def harvest_all(url, **kwargs):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'lxml')

    if page.status_code==200:
        content = soup.find('div', class_="row container-row").find('div', class_="subcontainer")
        title = content.find('h1', class_="page-header").text

        section = content.find('main', class_="main_content").find('div', class_="region region-content").find('section', {'id': 'block-system-main'})
        sectioncontent = section.find('div', class_="inner").find('div', class_="node node-article clearfix").find('div', class_="content")
        
        date = section.find('div', class_="field-name-field-publication-date").find('div', class_="field-item even").span['content']
        body = content.find("div", class_="field-name-body").find('div', property="content:encoded").text

        docparams = {
            'title': title,
            'owner_id': admin_id,
            'doc_url': url,
            'datasource': datasource,
            'date': date,
            'abstract': body,
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
    pass
