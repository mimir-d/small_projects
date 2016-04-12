
from http.server import BaseHTTPRequestHandler, HTTPServer
from sources.sample import SampleSource


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

        rss_data = rss.gen()
        self.wfile.write(rss_data)


if __name__ == '__main__':
    # since HTTPServer doesnt take handler instances, we need to put all this as a classmethod
    Handler.register_rss('/sample', SampleSource)

    HTTPServer.allow_reuse_address = False
    httpd = HTTPServer(('127.0.0.1', 9001), Handler)
    print('server starting')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print('server stopped')
