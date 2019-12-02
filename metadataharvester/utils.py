import os
import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geonode.settings")
if __name__ == '__main__':
    import django
    django.setup()

from geonode.documents.renderers import generate_thumbnail_content
from geonode.documents.models import Document

import requests
from cStringIO import StringIO

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

def save_document(docparams, specialparams, insertonly=False):
    '''
    save or update document
    '''
    try:
        doc = Document.objects.get(doc_url=docparams['doc_url'])
    except Document.DoesNotExist:
        print 'insert new Document:', docparams['doc_url']
        doc = Document(**docparams)
        mode = 'insert'
    else:
        if not insertonly:
            print 'update existing Document:', docparams['doc_url']
            for (key, value) in docparams.items():
                setattr(doc, key, value)
        mode = 'update'

    if (insertonly and mode == 'insert') or not insertonly:
        doc.save()

        if 'keywords' in specialparams:
            doc.keywords.add(*specialparams['keywords'])

        if 'creators' in specialparams:
            doc.creators.add(*specialparams['creators'])

    return mode

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
            print '%s.delay_seconds: %s' % (module, module.delay_seconds)
        else:
            return response

