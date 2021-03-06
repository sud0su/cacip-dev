'''
for first run call:
    harvest_all()
to update:
    harvest_latest()
'''

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","geonode.settings")
if __name__ == '__main__':
    import django
    django.setup()

from geonode.documents.models import Event
from sickle import Sickle, oaiexceptions
from tempfile import NamedTemporaryFile
from geonode.documents.renderers import generate_thumbnail_content
from PIL import Image
from cStringIO import StringIO
from bs4 import BeautifulSoup
from django.core.files.storage import default_storage as storage
from metadataharvester.utils import save_document, delayed_requests, create_thumbnail, BaseHarvester
from googletrans import Translator

import datetime
import json
import requests
import re
import time
import urlparse
import sys
import threading
import pychrome
import pytz

class Harvester(BaseHarvester):

    datezformat = '%Y-%m-%dT%H:%M:%SZ' # date format in UTC Z notation, Z=Zulu means UTC+0
    datasource = 'ctc-n.org/calendar/events'
    delay_seconds = 0
    delay_loop_seconds = 0
    thumb_name_tpl = 'document-{0}-thumb.png'
    index_url_tpl = 'https://www.ctc-n.org/api/events'
    harvest_choices_keys = ['harvest_all','harvest_latest']

    def harvest_all(self, **kwargs):
        offset = 0
        item_num = 0
        item_per_page = 5
        # translator = Translator()
        while True:
            index_page_response = requests.get(self.index_url_tpl.format())
            if index_page_response.status_code == 200:
                rows = json.loads(index_page_response.content)
                for row in rows:
                    # page_response = requests.get(row['Path'])
                    # soup = BeautifulSoup(page_response.content, 'html.parser')
                    # el = soup.find("div", {"class": "subcontainer"})
                    try:
                        pass
                        # avoid scrapping atm
                        # el_h1_title = el.select('h1.page-header')[0]
                        # el_span_datestart = el.select('span.date-display-start')[0]
                        # el_span_dateend= el.select('span.date-display-end')[0]
                        # el_img_thumbnail = el.select('div.field-type-image img')[0]
                        # el_div_abstract = el.select('div.field-type-text-with-summary div.field-item')[0]
                        # external_thumbnail_url = el_img_thumbnail.attrs['src']
                        # date_text = el_span_date.text.split(',')[1]
                    except Exception as identifier:
                        continue
                    else:
                        docparams = {
                            'doc_url': row['Path'],
                            'title': row['Title'],
                            # 'title': el_h1_title.text,
                            'owner_id': self.harvester_id,
                            # 'papersize':row[8],
                            'datasource': self.datasource,
                            'doc_type': self.doc_type,
                            'input_method': self.input_method,
                            # 'subtitle':row[12],
                            # 'category_id':row[5],
                            'date': None,
                            # 'date': datetime.datetime.utcnow().isoformat(),
                            # 'event_date_start': el_span_datestart.attrs['content'],
                            # 'event_date_end': el_span_dateend.attrs['content'],
                            # 'abstract': el_div_abstract.text,
                            'sourcetext': unicode(row),
                        }
                        specialparams = {
                            'keywords': [BeautifulSoup(kw, 'html.parser').text for kw in row['CTCN Keyword Matches']],
                            # 'creators': authors,
                            # 'external_thumbnail_url': urlparse.urljoin(docparams['doc_url'], external_thumbnail_url),
                        }
                        try:
                            doc = self.save_document(
                                docparams, 
                                specialparams, 
                                insertonly = kwargs.get('insertonly') or kwargs.get('insertnewonly'),
                                basemodel = Event
                            )

                            # if insertnewonly and document already exist then return
                            if kwargs.get('insertnewonly') and doc.save_mode == 'update':
                                print 'previous latest document: %s' % doc.doc_url
                                print 'new documents added:', item_num
                                return

                            # create_thumbnail(
                            #     doc_url = docparams['doc_url'], 
                            #     doc = None, 
                            #     external_thumbnail_url = specialparams['external_thumbnail_url']
                            # )
                        except Exception as identifier:
                            if kwargs.get('continue_on_error'):
                                self.delay_loop_seconds += 1
                                print str(identifier)
                                print 'continue next loop because continue_on_error=%s' % kwargs.get('continue_on_error')
                                print 'delay for %s seconds' % self.delay_loop_seconds
                                continue
                            else:
                                raise

                        item_num += 1
                        if kwargs.get('limit') and item_num >= kwargs.get('limit'):
                            return

                offset += item_per_page

            else:
                break

            # 1 loop only
            break

def pychrome_get(url):
    browser = pychrome.Browser()
    tab = browser.new_tab()
    eh = EventHandler(browser, tab)

    tab.start()

    tab.Page.stopLoading()
    tab.Page.enable()
    tab.url = url
    resp = eh.loadurl(url=url)
    # tab.Page.navigate(url=url)
    if resp.get('isloaded'):
        # read dom here
        pass
    return tab

    # tab.stop()
    # browser.close_tab(tab.id)

class EventHandler(object):
    pdf_lock = threading.Lock()

    def __init__(self, browser, tab, timeout = 60):
        self.browser = browser
        self.tab = tab
        self.timeout = timeout
        self.start_frame = None
        self.isloaded = True

        # attach event handler
        tab.Page.frameStartedLoading = self.frame_started_loading
        tab.Page.frameStoppedLoading = self.frame_stopped_loading

    def loadurl(self, url):
        self.tab.Page.navigate(url=url)
        start = time.time()
        while not self.isloaded :
            if time.time() - start > self.timeout:
                return {'istimeout': True}
            time.sleep(1)
        return {'isloaded': True}

    def frame_started_loading(self, frameId):
        self.isloaded = False
        if not self.start_frame:
            self.start_frame = frameId

    def frame_stopped_loading(self, frameId):
        if self.start_frame == frameId:
            self.tab.Page.stopLoading()
            self.isloaded = True

            # with self.pdf_lock:
            #     self.tab.stop()

def parse_date(datestr):
    dateformats = [
        "%A, %d %B %Y %H:%M",
        "%A, %B %d, %Y %H:%M",
    ]
    for dateformat in dateformats:
        try:
            date = datetime.datetime.strptime(datestr, dateformat)
        except ValueError as identifier: # incorrect date format
            continue # just try next format
        else:
            return date

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
