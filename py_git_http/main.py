# python 2.7

import os
import base64
from BaseHTTPServer import HTTPServer
from CGIHTTPServer import CGIHTTPRequestHandler

class Handler(CGIHTTPRequestHandler):
    KEYS = [
        'Basic %s' % base64.b64encode('me:a2lMfRd<w&avsYz/^1PxRN1l[w9W+xJ>')
    ]

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm="auth"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        auth = self.headers.getheader('Authorization')
        if auth is None:
            self.do_AUTHHEAD()
            self.wfile.write('no auth')
        elif auth in self.KEYS:
            CGIHTTPRequestHandler.do_GET(self)
        else:
            self.do_AUTHHEAD()
            self.wfile.write(auth)
            self.wfile.write('bad auth')

if __name__ == '__main__':
    try:
        PORT = int(os.getenv('PORT', 8080))
        httpd = HTTPServer(('', PORT), Handler)
        print 'listening on port', PORT
        httpd.serve_forever()
    except Exception as e:
        print 'exception', e
        raise
