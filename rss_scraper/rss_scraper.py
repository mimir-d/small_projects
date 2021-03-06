
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from urllib.parse import urlparse, parse_qsl

from sources.sample import SampleSource
from sources.thecodinglove import TheCodingLoveSource
from sources.youtube import YoutubeSource

from logger import log


class Handler(BaseHTTPRequestHandler):
    __rss = {}

    @classmethod
    def register_rss(cls, rss_class):
        cls.__rss[rss_class.RSS_ID] = rss_class

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/xml")
        self.end_headers()

    def do_GET(self):
        # first part of the url should be the rss identifier
        url = urlparse(self.path)
        rss_id, rss_path = re.match('/([^/]+)(.*)', url.path).groups()

        rss_class = self.__rss.get(rss_id, None)
        if rss_class is None:
            return self.send_error(404)

        self.send_response(200)
        self.send_header("Content-type", "text/xml")
        self.end_headers()

        try:
            rss = rss_class(rss_path, dict(parse_qsl(url.query)))
            self.wfile.write(rss.gen())
        except Exception as e:
            log.exception('Generate feed %s' % self.path)
            return self.send_error(400, 'Exception: %s' % e)


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass


if __name__ == '__main__':
    # since HTTPServer doesnt take handler instances, we need to put all this as a classmethod
    Handler.register_rss(SampleSource)
    Handler.register_rss(TheCodingLoveSource)
    Handler.register_rss(YoutubeSource)

    ThreadedHTTPServer.allow_reuse_address = False
    httpd = ThreadedHTTPServer(('127.0.0.1', 9001), Handler)
    print('server starting')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print('server stopped')
