
import requests


class RssSource(object):
    def __init__(self, rss):
        self.__rss = rss

    def _get_entries(self):
        '''
        Abstract method.
        Returns:
            list of rss entries
        '''
        raise NotImplementedError('abstract method')

    def gen(self):
        self.__rss.entry(self._get_entries(), replace=True)
        return self.__rss.rss_str()

    @property
    def url(self):
        return self.__rss.link()[0]['href']


class RssHtmlSource(RssSource):
    HTTP_HEADERS = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.8',
        'DNT': 1,
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
    }

    def _get_entries(self):
        html = requests.get(self.url, headers=self.HTTP_HEADERS).text
        return self._parse_html(html)

    def _parse_html(self, html):
        raise NotImplementedError
