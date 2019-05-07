#!/usr/bin/env python
# A simple script to suck up HTML, convert any images to inline Base64
# encoded format and write out the converted file.
#
# Usage: python standalone_html.py <input_file.html> <output_file.html>
#
# TODO: Consider MHTML format: https://en.wikipedia.org/wiki/MHTML

import os
# from bs4 import BeautifulSoup
from lxml import etree, html
from geonode.utils import linenum
import urllib3
import urlparse
import base64
import re
import mimetypes

def guess_type(filepath):
    """
    Return the mimetype of a file, given it's path.

    This is a wrapper around two alternative methods - Unix 'file'-style
    magic which guesses the type based on file content (if available),
    and simple guessing based on the file extension (eg .jpg).

    :param filepath: Path to the file.
    :type filepath: str
    :return: Mimetype string.
    :rtype: str
    """
    try:
        import magic  # python-magic
        return magic.from_file(filepath, mime=True)
    except ImportError:
        import mimetypes
        return mimetypes.guess_type(filepath)[0]

def file_to_base64(filepath):
    """
    Returns the content of a file as a Base64 encoded string.

    :param filepath: Path to the file.
    :type filepath: str
    :return: The file content, Base64 encoded.
    :rtype: str
    """
    import base64
    with open(filepath, 'rb') as f:
        encoded_str = base64.b64encode(f.read())
    return encoded_str


def make_html_images_inline(url):
    """
    Takes an HTML file and writes a new version with inline Base64 encoded
    images.

    :param in_filepath: Input file path (HTML)
    :type in_filepath: str
    :param out_filepath: Output file path (HTML)
    :type out_filepath: str
    """
    # basepath = os.path.split(in_filepath.rstrip(os.path.sep))[0]
    # soup = BeautifulSoup(open(in_filepath, 'r'), 'html.parser')
    urlparsed = urlparse.urlparse(url)
    http = urllib3.PoolManager()
    parser = etree.HTMLParser(remove_blank_text=True)
    htmltree = html.parse(url, parser=parser)
    for img in htmltree.findall(".//img"):
        img_path = urlparse.urlparse(img.attrib['src']).path
        img_url = urlparsed._replace(path=img_path)
        img_mimetype = mimetypes.guess_type(img_path)[0]
        img_data = http.request('GET', img_url.geturl()).data
        img.attrib['src'] = "data:%s;base64,%s" % (img_mimetype, base64.b64encode(img_data))

    htmlstring = etree.tostring(htmltree, pretty_print=False, with_tail=False)
    htmlstring_1line = re.sub(r"\r?\n|\r", '', htmlstring)

    return htmlstring_1line

    # with open(out_filepath, 'w') as of:
    #     of.write(str(soup))
