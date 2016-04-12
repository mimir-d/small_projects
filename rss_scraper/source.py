
import requests


class RssSource(object):
    def gen(self):
        raise NotImplementedError('abstract method')


class RssHtmlSource(RssSource):
    HTTP_HEADERS = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.8',
        'DNT': 1,
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
    }

    def __init__(self, rss):
        self.__rss = rss

    def _parse_html(self, data):
        raise NotImplementedError

    def gen(self):
        data = requests.get(self.__rss.link()[0]['href'], headers=self.HTTP_HEADERS).text
        self.__rss.entry(self._parse_html(data), replace=True)
        return self.__rss.rss_str()
