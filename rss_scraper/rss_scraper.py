
import re
import pytz
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from feedgen.entry import FeedEntry


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

        self.wfile.write(rss.gen())


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

    def _parse(self, data):
        raise NotImplementedError

    def gen(self):
        # uncomment this when using proper urls
        # data = requests.get(self.__rss.link, headers=self.HTTP_HEADERS).text
        data = '<html><body>rss</body></html>'

        self.__rss.entry(self._parse(data), replace=True)
        return self.__rss.rss_str()


class SomeSource(RssSource):
    def __init__(self):
        rss = FeedGenerator()
        rss.load_extension('dc')

        rss.title('Feed title')
        rss.link(href='Feed url', rel='self')
        rss.description('Feed description')

        super(SomeSource, self).__init__(rss)

    def _parse(self, data):
        soup = BeautifulSoup(data, 'html.parser')

        e = FeedEntry()
        e.load_extension('dc')

        e.title('title')
        e.link(href='link', rel='alternate')

        e.dc.dc_creator('author')
        e.description('description')
        e.content(soup.body.text, type='CDATA')
        e.pubdate(datetime.now(pytz.utc))

        return [e]


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
