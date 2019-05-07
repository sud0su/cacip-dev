#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''
print to pdf module using pychrome and chrome devtools
script based from:
    https://github.com/fate0/pychrome/blob/master/examples/multi_tabs_pdf.py
Debugging:
    run in terminal:
        export DEBUG=1
    in the same terminal start_django or import script in python shell, pychrome will print SEND and RECV data
    open localhost:9222, click on any link to open chromecast stream from remote headless chrome
    http://localhost:9222/json/protocol, chromedevtools capabilities
References:
    https://chromedevtools.github.io/devtools-protocol/tot
'''

from datetime import datetime, timedelta
from django.template import Context, Template
from geonode.htmlinline import make_html_images_inline
from geonode.utils import linenum
from PyPDF2 import PdfFileMerger, PdfFileReader
from StringIO import StringIO

import base64
import pychrome
import threading
import time

default_print_option = {

    # params for Page.printToPDF
    'displayHeaderFooter':True,
    'printBackground':True,
    'landscape':False,
    # 'scale':1,
    'marginTop':0.78,
    'marginBottom':0.3,
    'paperWidth':8.27,
    'paperHeight':11.69,
    'marginLeft':0.3,
    'marginRight':0.3,
    'pageRanges':"",
    # 'headerTemplate':"<span></span>",
    'footerTemplate':"<span></span>",

    # params for Emulation.setVisibleSize
    'screen-width':1024,
    'screen-height':1024,

    # used only in this script
    "javascript-delay":5,
    "timeout":30,
}

class EventHandler(object):
    pdf_lock = threading.Lock()

    def __init__(self, browser, tab):
        self.browser = browser
        self.tab = tab
        self.start_frame = None

    def frame_started_loading(self, frameId):
        if not self.start_frame:
            self.start_frame = frameId

    def frame_stopped_loading(self, frameId):

        if self.browser.print_option.get('javascript-delay'):
            time.sleep(self.browser.print_option.get('javascript-delay'))

        if self.start_frame == frameId:
            self.tab.Page.stopLoading()

            with self.pdf_lock:
                # must activate current tab
                url = self.tab.url

                url_header = self.browser.print_option['header-html']
                self.browser.print_option['headerTemplate'] = html_header = \
                    Template(make_html_images_inline(url_header)).render(Context(self.browser.print_option.get('headerparam',{})))

                # with open("header_inline.html", "wb") as fd:
                #     fd.write(html_header)

                ssdata = self.tab.Page.captureScreenshot()
                with open("%s.png" % (datetime.now().strftime('%c')), "wb") as fd:
                    fd.write(base64.b64decode(ssdata['data']))

                try:
                    self.tab.Emulation.setEmulatedMedia(
                        media="screen"
                    )
                    self.tab.printdata = data = self.tab.Page.printToPDF(**self.browser.print_option)

                    # with open("%s_%s.pdf" % (datetime.now().strftime('%c'), self.tab.id), "wb") as fd:
                    #     fd.write(base64.b64decode(data['data']))

                except Exception as e:
                    print linenum(), e
                finally:
                    self.tab.stop()

def close_all_tabs(browser):
    if len(browser.list_tab()) == 0:
        return

    for tab in browser.list_tab():
        try:
            tab.stop()
        except pychrome.RuntimeException:
            pass

        browser.close_tab(tab)

    time.sleep(1)
    assert len(browser.list_tab()) == 0

def print_from_urls(urls, print_option={}):
    browser = pychrome.Browser()
    browser.print_option = default_print_option.copy()
    browser.print_option.update(print_option)

    # close_all_tabs(browser)

    tabs = []
    for i in range(len(urls)):
        tabs.append(browser.new_tab())

    for i, tab in enumerate(tabs):
        eh = EventHandler(browser, tab)
        tab.Page.frameStartedLoading = eh.frame_started_loading
        tab.Page.frameStoppedLoading = eh.frame_stopped_loading

        tab.start()

        # tab.Emulation.setVisibleSize(
        #     width=browser.print_option.get('screen-width'),
        #     height=browser.print_option.get('screen-height')
        # )

        tab.Emulation.setDeviceMetricsOverride(
            width=browser.print_option.get('screen-width'),
            height=browser.print_option.get('screen-height'),
            deviceScaleFactor=0,
            mobile=False,
            viewport={
                'x':0,
                'y':0,
                'width':1024,
                'height':1024,
                'scale':1,
            },
        )

        tab.Page.stopLoading()
        tab.Page.enable()
        tab.url = urls[i]
        tab.Page.navigate(url=urls[i])

    # wait until all printdata ready or timeout reached
    time_limit = datetime.now() + timedelta(seconds=browser.print_option.get('timeout', 0))
    while True:
        all_printdata_ready = True
        for tab in tabs:
            try:
                tab.printdata['data']
            except Exception as e:
                all_printdata_ready = False
        if datetime.now() >= time_limit or all_printdata_ready:
            break
        time.sleep(1)

    # ensure close all tabs after timeout
    for tab in tabs:
        tab.stop()
        browser.close_tab(tab.id)

    merger = PdfFileMerger()
    for tab in tabs:
        try:
            tab.printdata['data']
        except Exception as e:
            continue
        else:
            merger.append(StringIO(base64.b64decode(tab.printdata['data'])))

    merged = StringIO()
    merger.write(merged)

    with open("%s.pdf" % datetime.now().strftime('%c'), "wb") as fd:
        fd.write(merged.getvalue())

    return merged.getvalue()
