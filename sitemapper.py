#!/usr/bin/env python
import time
import requests
import xml.etree.ElementTree as ET
import argparse
import logging
logger = logging.getLogger(__name__)

class XMLRetriever(object):
    """XMLRetriever class to make http queries and
    retrieve XML SiteMap File
    """
    def __init__(self, fullurl):
        """ __init__ accepts a fullurl string
        request(self)
        _extract_urls(self.fullurl)
        _extract_modified_header(self, req)
        get_data(self)
        """
        self.fullurl = fullurl
        self.urls = []
        self.last_modified = ''
    def request(self):
        """ request(self) makes a single http request to get sitemap.xml
        """
        r = requests.get(self.fullurl)
        self._extract_urls(r)
        self._extract_headers(r)
    def _extract_urls(self, request):
        """
        Extract each url from the sitemap.xml file
        """
        root = ET.fromstring(request.content)
        self.urls = [child[0].text for child in root]
        # for child in root:
        #     self.urls.append(child[0].text)
    def _extract_headers(self, req):
        """
        extract the header 'last-modified' might be of use at some point
        """
        last_modified = req.headers['last-modified']
        # cached = req.headers['X-Apublish-Id']
        self.last_modified = last_modified
    def get_data(self):
        """
        get_data
        return a tuple as follows
        self.last_modified string
        self.urls a list of all the urls in the sitemap.xml file
        """
        return self.last_modified, self.urls

class ProcSiteMap(object):
    """ ProcSiteMap process the sitemap list
    __init__(urls)
    connect(self)
    """
    def __init__(self, urls):
        self.urls = urls
    def connect(self):
        for url in self.urls:
            status, total_time, cached = self._connect(url)
            log = 'URL:{0} Latency:{1} Code:{2} Cached:{3}'.format(url, total_time, status, cached)
            logging.info('%s', log)

            time.sleep(5)

    def _connect(self, url):
        millis_start = int(round(time.time() * 1000))
        r = requests.get(url, headers = {'user-agent':'Acadaca'})
        millis_end = int(round(time.time() * 1000))
        total_time = millis_end - millis_start
        try:
            r.headers['X-Apublish-Id']
            cached = 'Yes'
        except Exception:
            cached = 'No'
        status = r.status_code
        return status, total_time, cached
        
def main(full_url, log):
    logging.basicConfig(filename=log, format='%(asctime)s %(message)s', level=logging.INFO)
    
    url = full_url
    xml_retriever = XMLRetriever(url)
    xml_retriever.request()
    _, urls_list = xml_retriever.get_data()
    sitemap = ProcSiteMap(urls_list)
    sitemap.connect()
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Retrieve sitemap.xml from a site and make an HTTP request for each entry')
    parser.add_argument('-u', '--URL', dest='url', help='sitemap.xml file location such as http://www.test.com/sitemap.xml', required=True, default=None)    
    parser.add_argument('-l', '--Log', dest='log', help='Log file to store log information', required=True, default='/tmp/sitemap.log')

    args = parser.parse_args()
    url = args.url
    log = args.log
    
    main(url, log)
    