
import pytz
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from feedgen.entry import FeedEntry

from source import RssHtmlSource


class SampleSource(RssHtmlSource):
    def __init__(self):
        rss = FeedGenerator()
        rss.load_extension('dc')

        rss.title('Feed title')
        rss.link(href='http://example.com', rel='self')
        rss.description('Feed description')

        super(SampleSource, self).__init__(rss)

    def _parse_html(self, data):
        soup = BeautifulSoup(data, 'html.parser')

        ret = []
        for i, li in enumerate(soup.find_all('p')):
            e = FeedEntry()
            e.load_extension('dc')

            e.title('title: <p> #%d' % i)
            e.link(href='http://%d.example.com' % i, rel='alternate')

            e.dc.dc_creator('author')
            e.description('description: <p> #%d' % i)
            e.content('content: %s' % li.text, type='CDATA')
            e.pubdate(datetime.now(pytz.utc) + timedelta(minutes=i))

            ret.append(e)

        return ret
