
from os import path
import re
import string
import dateutil.parser as dateparser
from feedgen.feed import FeedGenerator
from feedgen.entry import FeedEntry
from apiclient.discovery import build as youtube_build

from source import RssSource
from logger import log

# disable oauth2 lock warnings from multithreading
import logging
logging.getLogger('oauth2client.contrib.locked_file').setLevel(logging.ERROR)


class YoutubeSource(RssSource):
    RSS_ID = 'youtube'

    __YOUTUBE_API_SERVICE_NAME = "youtube"
    __YOUTUBE_API_VERSION = "v3"
    with open(path.join(path.dirname(path.abspath(__file__)), 'youtube.key')) as f:
        __API_KEY = f.read().strip()

    __PLAYLIST_URL = 'https://www.youtube.com/playlist?list=%s'
    __VIDEO_URL = 'https://www.youtube.com/watch?v=%s'

    # gruber url regex
    # http://stackoverflow.com/questions/1986059/gruber-s-url-regular-expression-in-python
    __URL_RE = r'\b(([\w-]+://?|www[.])[^\s()<>]+(?:\([\w\d]+\)|([^%s\s]|/)))' % re.escape(string.punctuation)

    __CONTENT = '''
        <p><img src='%(image)s'/></p>
        <p>%(content)s</p>
    '''

    def __init__(self, rss_path, rss_params):
        super(YoutubeSource, self).__init__(rss_path, rss_params)

        self.__api = youtube_build(
            self.__YOUTUBE_API_SERVICE_NAME, self.__YOUTUBE_API_VERSION,
            developerKey=self.__API_KEY
        )

    # TODO: this could be cached
    def __get_channel_details(self, rss_path):
        # path = /youtube/channel/<id>
        # path = /youtube/user/<id>
        parts = rss_path.split('/')[1:]
        if parts[0] == 'channel':
            req = self.__api.channels().list(part='snippet,contentDetails', id=parts[1])
        elif parts[0] == 'user':
            req = self.__api.channels().list(part='snippet,contentDetails', forUsername=parts[1])

        try:
            data = req.execute()['items'][0]
            return (
                data['snippet']['title'],
                data['snippet']['description'],
                data['contentDetails']['relatedPlaylists']['uploads']
            )
        except:
            log.exception()
            raise ValueError('invalid rss path type')

    def __parse_content(self, snippet):
        desc = re.sub(self.__URL_RE, r'<a href="\1">\1</a>', snippet['description'])
        return '<br>'.join(desc.split('\n'))

    def _get_header(self):
        title, desc, self.__uploads_id = self.__get_channel_details(self._rss_path)
        rss = FeedGenerator()
        rss.load_extension('dc')

        rss.title(title)
        rss.link(href=self.__PLAYLIST_URL % self.__uploads_id, rel='self')
        rss.description(desc or title)

        return rss

    def _get_entries(self):
        playlist = self.__api.playlistItems().list(
            playlistId=self.__uploads_id,
            part="snippet",
            maxResults=20
        ).execute()

        ret = []
        for item in playlist['items']:
            snip = item['snippet']
            e = FeedEntry()
            e.load_extension('dc')

            e.dc.dc_creator('none')
            e.title(snip['title'])
            e.link(href=self.__VIDEO_URL % snip['resourceId']['videoId'], rel='alternate')
            e.description(snip['title'])
            e.pubdate(dateparser.parse(snip['publishedAt']))

            content_args = {
                'image': snip['thumbnails']['high']['url'],
                'content': self.__parse_content(snip)
                # TODO: some comments i think?
                # 'comments':
            }
            e.content(self.__CONTENT % content_args, type='CDATA')
            ret.append(e)

        return ret

# TODO: add request throttler per 100s (since youtube limits)
