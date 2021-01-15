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
            parsed_feed_url = feedparser.parse(rss_feed_url)
            rss_raw_entries = parsed_feed_url['entries']
            if not rss_raw_entries:
                continue

            episode_count = self.anime.episode_count  # episode_count can be null in API
            if episode_count is None:
                episode_count = self.progress + 1

            for episode_no in range(self.progress + 1, episode_count+1):
                episode_entries = []
                cleaned_title = re.sub(r'\:|\-|\s', '', title)
                if self.anime.is_movie:
                    regex = '.*{0}.*\.({1})$'.format(cleaned_title, '|'.join(video_extensions))
                else:
                    regex = '{0}(S\d+E)?({1:02d}|{1}).*(\.({2}))?$'.format(cleaned_title, episode_no, '|'.join(video_extensions))

                for rss_raw_entry in rss_raw_entries:
                    cleaned_rss_title = re.sub(r'\s?[\[\(\{](.*?)[\]\)\}]\s?', '', rss_raw_entry.title)
                    cleaned_rss_title = re.sub('-|\s|\:', '', cleaned_rss_title)
                    if re.match(regex, cleaned_rss_title):
                        print('Found a match for anime pattern "{}": "{}", no: {}, "{}" seeds'.format(regex, title, episode_no, rss_raw_entry.title))
                        episode_entries.append(RSSEntry(rss_raw_entry))

                if episode_entries:
                    episode_entries.sort()
                    entries.append(episode_entries[0])
                else:
                    break  # don't check higher episode count, as it is most possible that they are not released yet

            if entries:
                break  # don't check other titles if one resulted in valid entries

        return entries
