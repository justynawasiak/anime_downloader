import re
import feedparser
import requests
import urllib.parse
from anime import Anime
from rssEntry import RSSEntry


class LibraryEntry:
    RSS_FEED_URL = 'https://nyaa.si/?page=rss&c=1_2&q={}'

    def __init__(self, json):
        self.id = json['id']
        self.progress = json['attributes']['progress']
        self.status = json['attributes']['status'].lower()
        if self.status not in ['current', 'planned']:
            raise Exception()
        print("\nLibraryEntry: id {}, status {}, progress {}".format(self.id, self.status, self.progress))

        anime_link = json['relationships']['anime']['links']['related']
        print('Fetching anime info from {}'.format(anime_link))

        anime_json = requests.get(anime_link).json()
        self.anime = Anime(anime_json['data'])
        self.rss_entries = self.rss_find_entries_by_titles(self.anime.get_titles())

    def rss_find_entries_by_titles(self, titles):
        entries = []
        video_extensions = ['mkv', 'avi', 'mp4']

        for title in titles:
            rss_feed_url = LibraryEntry.RSS_FEED_URL.format(urllib.parse.quote(title))
            print("Fetching rss feed {} ".format(rss_feed_url))
            rss_raw_entries = feedparser.parse(rss_feed_url)['entries']
            rss_channel_title = feedparser.parse(rss_feed_url)['channel']['title']

            episode_count = self.anime.episode_count  # episode_count can be null in API
            if episode_count is None:
                episode_count = self.progress + 1

            for episode_no in range(self.progress + 1, episode_count+1):
                if self.anime.is_movie:
                    regex = '.*\.({0})$'.format('|'.join(video_extensions))
                else:
                    regex = '.* - ({0:02d}|{1}).*(\.({1}))?$'.format(episode_no, '|'.join(video_extensions))

                episode_entries = []
                channel_title_regex = '.*- "{0}" -.*'.format(title)

                for rss_raw_entry in rss_raw_entries:
                    if re.match(channel_title_regex, rss_channel_title):
                        if re.match(regex, rss_raw_entry.title):
                            print('Found a match for channel title pattern "{}": "{}", no: {}, "{}", {} seeds'.format(regex, title, episode_no, rss_raw_entry.title, rss_raw_entry.nyaa_seeders))
                            episode_entries.append(RSSEntry(rss_raw_entry))
                            break
                        if re.match(regex, rss_raw_entry.title):
                            print('Found a match for entry title pattern "{}": "{}", no: {}, "{}", {} seeds'.format(regex, title,
                                                                                                        episode_no,
                                                                                                        rss_raw_entry.title,
                                                                                                        rss_raw_entry.nyaa_seeders))
                            episode_entries.append(RSSEntry(rss_raw_entry))

                if episode_entries:
                    episode_entries.sort()
                    entries.append(episode_entries[0])

        return entries
