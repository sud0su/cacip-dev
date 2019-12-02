# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2016 OSGeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

import os, sys


path='/Users/immap/Documents/Project/CACIP/CACIP-Dev'

if path not in sys.path:
  sys.path.append(path)

from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geonode.settings")

# This application object is used by the development server
# as well as any WSGI server configured to use this file.

application = get_wsgi_application()

# import threading
# import pprint
# import time
# import os

# class LoggingInstance:
#     def __init__(self, start_response, oheaders, ocontent):
#         self.__start_response = start_response
#         self.__oheaders = oheaders
#         self.__ocontent = ocontent

#     def __call__(self, status, headers, *args):
#         pprint.pprint(((status, headers)+args), stream=self.__oheaders)
#         self.__oheaders.close()

#         self.__write = self.__start_response(status, headers, *args)
#         return self.write

#     def __iter__(self):
#         return self

#     def write(self, data):
#         self.__ocontent.write(data)
#         self.__ocontent.flush()
#         return self.__write(data)

#     def next(self):
#         data = self.__iterable.next()
#         self.__ocontent.write(data)
#         self.__ocontent.flush()
#         return data

#     def close(self):
#         if hasattr(self.__iterable, 'close'):
#             self.__iterable.close()
#         self.__ocontent.close()

#     def link(self, iterable):
#         self.__iterable = iter(iterable)

# class LoggingMiddleware:

#     def __init__(self, application, savedir):
#         self.__application = application
#         self.__savedir = savedir
#         self.__lock = threading.Lock()
#         self.__pid = os.getpid()
#         self.__count = 0

#     def __call__(self, environ, start_response):
#         self.__lock.acquire()
#         self.__count += 1
#         count = self.__count
#         self.__lock.release()

#         key = "%s-%s-%s" % (time.time(), self.__pid, count)

#         iheaders = os.path.join(self.__savedir, ".iheaders")
#         iheaders_fp = file(iheaders, 'w')

#         icontent = os.path.join(self.__savedir, ".icontent")
#         icontent_fp = file(icontent, 'w+b')

#         oheaders = os.path.join(self.__savedir, ".oheaders")
#         oheaders_fp = file(oheaders, 'w')

#         ocontent = os.path.join(self.__savedir, ".ocontent")
#         ocontent_fp = file(ocontent, 'w+b')

#         errors = environ['wsgi.errors']
#         pprint.pprint(environ, stream=iheaders_fp)
#         iheaders_fp.close()

#         length = int(environ.get('CONTENT_LENGTH', '0'))
#         input = environ['wsgi.input']
#         while length != 0:
#             data = input.read(min(4096, length))
#             if data:
#                 icontent_fp.write(data)
#                 length -= len(data)
#             else:
#                 length = 0
#         icontent_fp.flush()
#         icontent_fp.seek(0, os.SEEK_SET)
#         environ['wsgi.input'] = icontent_fp

#         iterable = LoggingInstance(start_response, oheaders_fp, ocontent_fp)
#         iterable.link(self.__application(environ, iterable))
#         return iterable

# application = LoggingMiddleware(application, '/home/ubuntu/tmp/')