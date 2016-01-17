
import re
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

import requests
from bs4 import BeautifulSoup
import PyRSS2Gen as pyrss


class Handler(BaseHTTPRequestHandler):
    __rss = {}

    @classmethod
    def register_rss(cls, path, rss):
        cls.__rss[path] = rss()

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/xml")
        self.end_headers()

    def do_GET(self):
        rss = self.__rss.get(self.path, None)
        if rss is None:
            return self.send_error(404)

        self.send_response(200)
        self.send_header("Content-type", "text/xml")
        self.end_headers()

        rss.run(self.wfile)


class RssSource(object):
    HTTP_HEADERS = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.8',
        'DNT': 1,
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
    }

    def __init__(self, rss):
        self.__rss = rss

    def __request(self):
        return requests.get(self.__rss.link, headers=self.HTTP_HEADERS).text

    def _parse(self, data):
        raise NotImplementedError

    def run(self, fd):
        self.__rss.items = self._parse(self.__request())
        self.__rss.write_xml(fd)


class SomeSource(RssSource):
    def __init__(self):
        rss = pyrss.RSS2(
            title='Feed title',
            link='Feed url',
            description='Feed description',
            lastBuildDate=datetime.now()
        )
        super(SomeSource, self).__init__(rss)

    def _parse(self, data):
        soup = BeautifulSoup(data, 'html.parser')

        # imagine parsing the soup here and return a list of
        # pyrss.RSSItem(
        #     title='item title',
        #     link='item url',
        #     description='item content',
        #     pubDate=datetime.now()
        # )

        return []


if __name__ == '__main__':
    # since HTTPServer doesnt take handler instances, we need to put all this as a classmethod
    Handler.register_rss('/local_some', SomeSource)

    httpd = HTTPServer(('127.0.0.1', 9001), Handler)
    print('server starting')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print('server stopped')
