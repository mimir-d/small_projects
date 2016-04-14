
import pytz
from datetime import datetime
import requests
from lxml import etree
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from feedgen.entry import FeedEntry
from feedgen.ext.dc import DcBaseExtension

from source import RssSource, RssHtmlSource


class TheCodingLoveSource(RssSource):
    RSS_ID = 'thecodinglove'
    __URL = 'http://thecodinglove.com'
    __HTTP_HEADERS = {
        'Accept-Encoding': 'gzip, deflate',
        'User-Agent': 'RSSOwl/2.1.6.201212081830 (Windows; U; en)'
    }
    __DC_NS = DcBaseExtension().extend_ns()['dc']
    __TIME_FORMAT = '%a, %d %b %Y %H:%M:%S %z'

    def __get_xml(self):
        rss = requests.get('%s/rss' % self.__URL, headers=self.__HTTP_HEADERS).text
        return etree.fromstring(rss.encode('utf8'))

    def __get_xml_dict(self, node, names):
        return {n: node.find(n).text for n in names}

    def __get_html_content(self, item_url):
        html = requests.get(item_url, headers=RssHtmlSource.HTTP_HEADERS).text
        soup = BeautifulSoup(html, 'html.parser')
        return str(soup.find(class_='post', id='post1'))

    def _get_header(self):
        rss = FeedGenerator()
        rss.load_extension('dc')

        # channel xml tags
        chan_details = self.__get_xml_dict(
            self.__rss_xml.find('channel'),
            ['title', 'description', 'link']
        )

        rss.title(chan_details['title'])
        rss.link(href=chan_details['link'], rel='self')
        rss.description(chan_details['description'])

        return rss

    def _get_entries(self):
        ret = []

        chan_tag = self.__rss_xml.find('channel')
        for item_tag in chan_tag.findall('item'):
            e = FeedEntry()
            e.load_extension('dc')

            item_details = self.__get_xml_dict(
                item_tag,
                ['title', 'link', 'guid', 'pubDate', '{%s}creator' % self.__DC_NS]
            )

            e.title(item_details['title'])
            e.link(href=item_details['link'], rel='alternate')
            e.guid(item_details['guid'])
            e.dc.dc_creator(item_details['{%s}creator' % self.__DC_NS])
            e.pubdate(datetime.strptime(item_details['pubDate'], self.__TIME_FORMAT))
            e.content('<p>%s</p>' % self.__get_html_content(item_details['link']), type='CDATA')

            ret.append(e)

        return ret

    def gen(self):
        # maybe do this differently? while, at the same time, keeping the single request method
        # on target site -mimir
        self.__rss_xml = self.__get_xml()
        return super().gen()
