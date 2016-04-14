
import requests


class RssSource(object):
    def __init__(self, rss_path, rss_params):
        self._rss_path = rss_path
        self._rss_params = rss_params

    def _get_header(self):
        '''
        Abstract method.
        Returns:
            rss header object
        '''
        raise NotImplementedError('abstract method')

    def _get_entries(self):
        '''
        Abstract method.
        Returns:
            list of rss entries
        '''
        raise NotImplementedError('abstract method')

    def gen(self):
        rss = self._get_header()
        rss.entry(self._get_entries(), replace=True)
        return rss.rss_str()


class RssHtmlSource(RssSource):
    HTTP_HEADERS = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.8',
        'DNT': 1,
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
    }
    def __init__(self, url, rss_path, rss_params):
        super().__init__(rss_path, rss_params)
        self.__url = url

    def _get_entries(self):
        html = requests.get(self.__url, headers=self.HTTP_HEADERS).text
        return self._parse_html(html)

    def _parse_html(self, html):
        raise NotImplementedError
