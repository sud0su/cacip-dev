'''
utils for wsgi debugging
https://modwsgi.readthedocs.io/en/develop/user-guides/debugging-techniques.html
'''

import threading
import pprint
import time
import os

class LoggingInstance:
    def __init__(self, start_response, oheaders, ocontent):
        self.__start_response = start_response
        self.__oheaders = oheaders
        self.__ocontent = ocontent

    def __call__(self, status, headers, *args):
        pprint.pprint(((status, headers)+args), stream=self.__oheaders)
        self.__oheaders.close()

        self.__write = self.__start_response(status, headers, *args)
        return self.write

    def __iter__(self):
        return self

    def write(self, data):
        self.__ocontent.write(data)
        self.__ocontent.flush()
        return self.__write(data)

    def next(self):
        data = self.__iterable.next()
        self.__ocontent.write(data)
        self.__ocontent.flush()
        return data

    def close(self):
        if hasattr(self.__iterable, 'close'):
            self.__iterable.close()
        self.__ocontent.close()

    def link(self, iterable):
        self.__iterable = iter(iterable)

class LoggingMiddleware:
    '''
    doc:
    https://modwsgi.readthedocs.io/en/develop/user-guides/debugging-techniques.html#tracking-request-and-response
    usage:
        in wsgi.py:
            application = LoggingMiddleware(application, '/tmp/')
        view output:
            /tmp/.iheaders
            /tmp/.icontent
            /tmp/.oheaders
            /tmp/.ocontent
    '''

    def __init__(self, application, savedir):
        self.__application = application
        self.__savedir = savedir
        self.__lock = threading.Lock()
        self.__pid = os.getpid()
        self.__count = 0

    def __call__(self, environ, start_response):
        self.__lock.acquire()
        self.__count += 1
        count = self.__count
        self.__lock.release()

        key = "%s-%s-%s" % (time.time(), self.__pid, count)

        iheaders = os.path.join(self.__savedir, ".iheaders")
        iheaders_fp = file(iheaders, 'w')

        icontent = os.path.join(self.__savedir, ".icontent")
        icontent_fp = file(icontent, 'w+b')

        oheaders = os.path.join(self.__savedir, ".oheaders")
        oheaders_fp = file(oheaders, 'w')

        ocontent = os.path.join(self.__savedir, ".ocontent")
        ocontent_fp = file(ocontent, 'w+b')

        errors = environ['wsgi.errors']
        pprint.pprint(environ, stream=iheaders_fp)
        iheaders_fp.close()

        length = int(environ.get('CONTENT_LENGTH', '0'))
        input = environ['wsgi.input']
        while length != 0:
            data = input.read(min(4096, length))
            if data:
                icontent_fp.write(data)
                length -= len(data)
            else:
                length = 0
        icontent_fp.flush()
        icontent_fp.seek(0, os.SEEK_SET)
        environ['wsgi.input'] = icontent_fp

        iterable = LoggingInstance(start_response, oheaders_fp, ocontent_fp)
        iterable.link(self.__application(environ, iterable))
        return iterable

class Debugger:
    '''
    Doc:
    https://modwsgi.readthedocs.io/en/develop/user-guides/debugging-techniques.html#python-interactive-debugger
    Usage:
        in wsgi.py:
            application = Debugger(application)
        in apache.conf:
            ErrorLog /dev/stdout
        in terminal:
            sudo apache2ctl -X
    '''    

    def __init__(self, object):
        self.__object = object

    def __call__(self, *args, **kwargs):
        import pdb, sys
        debugger = pdb.Pdb()
        debugger.use_rawinput = 0
        debugger.reset()
        sys.settrace(debugger.trace_dispatch)

        try:
            return self.__object(*args, **kwargs)
        finally:
            debugger.quitting = 1
            sys.settrace(None)
