from HTMLParser import HTMLParser
import os
import requests
import urllib2
from urlparse import urlparse

from slam.utils.logging_utils import get_logger


class URLHTMLParser(HTMLParser, object):
    
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            attrs_map = dict(attrs)
            url = attrs_map.get('href')
            self.urls.add(url)
    
    def feed(self, html_source):
        self.urls = set()
        super(URLHTMLParser, self).feed(html_source)
        return list(self.urls)

logger = get_logger()

def fetch_all_files_from_url(base_url, out_folder, extension):
    chunk_size = 20 * 4096
    parsed_uri = urlparse(base_url)
    url_domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    
    html_source = requests.get(base_url).content
    url_parser = URLHTMLParser()
    urls = url_parser.feed(html_source)
    urls = [url for url in urls if url and not url.startswith('#')]
    for i, url in enumerate(urls):
        logger.info('processing url:{}'.format(url))
        if not url.startswith('http') or not url.startswith('https'):
            urls[i] = url_domain + url
    
    filtered_urls = [url for url in urls if url.endswith(extension) ]
    for url in filtered_urls:
        file_name = url.split('/')[-1]
        logger.info('downloading file at {} and saving as {}'.format(url, file_name))
        response = urllib2.urlopen(url)
        with open(os.path.join(out_folder, file_name), 'wb') as f:
            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)

if __name__ == '__main__':
    output_folder = '/home/sanjeev/data'
    url = 'http://vision.in.tum.de/data/datasets/rgbd-dataset/download'
    fetch_all_files_from_url(url, output_folder, extension='tgz')

