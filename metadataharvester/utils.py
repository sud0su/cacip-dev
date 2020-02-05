import os
import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geonode.settings")
if __name__ == '__main__':
    import django
    django.setup()

from cStringIO import StringIO
from geonode.base.models import Region
from geonode.documents.renderers import generate_thumbnail_content
from geonode.documents.models import Document
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from argparse import RawTextHelpFormatter
from django.contrib.auth import get_user_model

import requests
import time
import argparse

thumb_name_tpl = 'document-{0}-thumb.png'

def create_thumbnail(doc_url, doc, external_thumbnail_url):
    '''
    create document thumbnail
    '''

    img_response = delayed_requests({'args': [external_thumbnail_url], 'kwargs': {
                                    'allow_redirects': True}}, module=sys.modules[__name__])
    if img_response.status_code == 200:
        doc = doc or Document.objects.get(doc_url=doc_url)
        doc.save_thumbnail(
            filename=thumb_name_tpl.format(doc.uuid),
            image=generate_thumbnail_content(StringIO(img_response.content), size=(600, 450))
        )
    else:
        print 'img_response.status_code:', img_response.status_code

def save_document(docparams, specialparams, insertonly=False, basemodel=Document):
    '''
    save or update document
    '''
    try:
        doc = basemodel.objects.get(doc_url=docparams['doc_url'])
    except basemodel.DoesNotExist:
        print 'insert new Document:', docparams['doc_url']
        doc = basemodel(**docparams)
        setattr(doc, 'save_mode', 'insert')
    else:
        if not insertonly:
            print 'update existing Document:', docparams['doc_url']
            for (key, value) in docparams.items():
                setattr(doc, key, value)
        setattr(doc, 'save_mode', 'update')

    if (insertonly and doc.save_mode == 'insert') or not insertonly:
        doc.save()

        # create_thumbnail(docparams['doc_url'])

        if 'keywords' in specialparams:
            doc.keywords.add(*specialparams['keywords'])

        if 'creators' in specialparams:
            doc.creators.add(*specialparams['creators'])

        if 'regions' in specialparams:
            regions = Region.objects.filter(name__in=specialparams['regions'])
            doc.regions.add(*regions)

        # valid_keywords = filter(None, row[7].split("-"))
        # doc.keywords.add(*valid_keywords)
        # row[16] = doc.id
        # loc = Region.objects.get(pk=row[4])
        # doc.regions.add(loc)
    return doc

def delayed_requests(requestsparams, module=sys.modules[__name__]):
    '''
    request with delay time to work around rate limiter
    '''
    if not hasattr(module, 'delay_seconds'):
        setattr(module, 'delay_seconds', 0)

    while True:
        if getattr(module, 'delay_seconds'):
            print 'wait for %s seconds' % module.delay_seconds
            time.sleep(module.delay_seconds)
        response = requests.get(*requestsparams.get('args', []), **requestsparams.get('kwargs', {}))
        if response.status_code == 429:  # rate limited
            module.delay_seconds += 1
            print '%s.delay_seconds: %s' % (module.__name__, module.delay_seconds)
        else:
            return response

class BaseHarvester(object):

    harvester_username = 'harvester'
    harvester_id = get_user_model().objects.get(username=harvester_username).id
    thumb_name_tpl = 'document-{0}-thumb.png'
    delay_seconds = 0
    harvest_choices_all = {
        'harvest_all': {
            'handler': 'harvest_all',
            'help': 'harvest_all: harvest resources, insert new and update existing',
        }, 
        'harvest_new': {
            'handler': 'harvest_new',
            'help': 'harvest_new: harvest resources, insert new only',
        }, 
        'harvest_latest': {
            'handler': 'harvest_latest',
            'help': 'harvest_latest: harvest resources, insert new, exit on exist',
        }
    }
    harvest_choices_keys = harvest_choices_all.keys()
    input_method = 'harvested'
    doc_type = 'publications'

    def dispatch_args(self, harvest_choices_keys=harvest_choices_keys):
        '''
        dispatch command line arguments to their respective handler
        '''

        harvest_choices = {k:v for k,v in self.harvest_choices_all.items() if k in harvest_choices_keys}
        parser = argparse.ArgumentParser(description='Harvest resources.', formatter_class=RawTextHelpFormatter)

        parser.add_argument(
            'harvest_type', 
            # choices = ['harvest_all', 'harvest_new', 'harvest_latest'],
            # help = 'harvest_all: harvest resources, insert new and update existing'
            #     '\nharvest_new: harvest resources, insert new only'
            #     '\nharvest_latest: harvest resources, insert new, exit on exist'
            choices = harvest_choices.keys(),
            help = '\n'.join([v['help'] for k,v in harvest_choices.items()])
        )
        
        args = parser.parse_args()

        if args.harvest_type in harvest_choices:
            handler = harvest_choices[args.harvest_type].get('handler')
            if hasattr(self, handler):
                getattr(self, handler)()

        # if args.harvest_type == "harvest_all":
        #     self.harvest_all()
        # elif args.harvest_type == "harvest_new":
        #     self.harvest_new()
        # elif args.harvest_type == "harvest_latest":
        #     self.harvest_latest()
            
    def create_thumbnail(self, doc_url, doc, external_thumbnail_url):
        '''
        create document thumbnail
        '''

        img_response = self.delayed_requests({
            'args': [external_thumbnail_url], 
            'kwargs': {
                'allow_redirects': True
            }
        })

        if img_response.status_code == 200:
            doc = doc or Document.objects.get(doc_url=doc_url)
            doc.save_thumbnail(
                filename=self.thumb_name_tpl.format(doc.uuid),
                image=generate_thumbnail_content(StringIO(img_response.content), size=(600, 450))
            )
        else:
            print 'img_response.status_code:', img_response.status_code

    def save_document(self, docparams, specialparams, insertonly=False, basemodel=Document):
        '''
        save or update document
        '''
        try:
            doc = basemodel.objects.get(doc_url=docparams['doc_url'])
        except basemodel.DoesNotExist:
            print 'insert new Document:', docparams['doc_url']
            doc = basemodel(**docparams)
            setattr(doc, 'save_mode', 'insert')
        else:
            if not insertonly:
                print 'update existing Document:', docparams['doc_url']
                for (key, value) in docparams.items():
                    setattr(doc, key, value)
            setattr(doc, 'save_mode', 'update')

        if (insertonly and doc.save_mode == 'insert') or not insertonly:
            doc.save()

            # create_thumbnail(docparams['doc_url'])

            if 'keywords' in specialparams:
                doc.keywords.add(*specialparams['keywords'])

            if 'creators' in specialparams:
                doc.creators.add(*specialparams['creators'])

            if 'regions' in specialparams:
                regions = Region.objects.filter(name__in=specialparams['regions'])
                doc.regions.add(*regions)

            # valid_keywords = filter(None, row[7].split("-"))
            # doc.keywords.add(*valid_keywords)
            # row[16] = doc.id
            # loc = Region.objects.get(pk=row[4])
            # doc.regions.add(loc)
        return doc

    def delayed_requests(self, requestsparams, module=sys.modules[__name__]):
        '''
        request with delay time to work around rate limiter
        '''
        if not hasattr(self, 'delay_seconds'):
            setattr(self, 'delay_seconds', 0)

        while True:
            if getattr(self, 'delay_seconds'):
                print 'wait for %s seconds' % self.delay_seconds
                time.sleep(self.delay_seconds)
            response = requests.get(*requestsparams.get('args', []), **requestsparams.get('kwargs', {}))
            if response.status_code == 429:  # rate limited
                self.delay_seconds += 1
                print '%s.delay_seconds: %s' % (self.__name__, self.delay_seconds)
            else:
                return response

    def get_session(self, *args, **kwargs):
        session = requests.Session()

        retries = kwargs.get('retries', Retry(
            total = kwargs.get('retries_total', 3),
            backoff_factor = kwargs.get('retries_backoff_factor', 1),
            status_forcelist = kwargs.get('retries_status_forcelist', [ 500, 502, 503, 504 ])))

        session.mount('http://', HTTPAdapter(max_retries=retries))

        return session

    def harvest_all(self, *args, **kwargs):
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
        raise NotImplementedError

    def harvest_latest(self):
        self.harvest_all(insertnewonly=True)

    def harvest_new(self):
        self.harvest_all(insertonly=True)
