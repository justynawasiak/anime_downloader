import re
from time import sleep
import urllib.parse
from urllib.parse import urlparse

import feedparser
import requests

from anime import Anime
from rssEntry import RSSEntry


class LibraryEntry:
    RSS_FEED_URL = 'https://nyaa.si/?page=rss&c=1_2&q={}'
    ALLOWED_STATUSES = {'current', 'planned'}

    def __init__(self, json, session=None, **_kwargs):
        self.session = session or requests.Session()
        self.id = json['id']
        self.progress = json['attributes']['progress']
        self.status = json['attributes']['status'].lower()
        if self.status not in self.ALLOWED_STATUSES:
            raise ValueError(f"Skipping library entry {self.id} with status={self.status!r}")
        print("\nLibraryEntry: id {}, status {}, progress {}".format(self.id, self.status, self.progress))

        anime_link = json['relationships']['anime']['links']['related']
        print('Fetching anime info from {}'.format(anime_link))

        anime_json = self._get_json_with_retries(anime_link)
        self.anime = Anime(anime_json['data'])
        self.rss_entries = self._rss_find_entries_by_titles(self.anime.get_titles())

    @staticmethod
    def _is_allowed_kitsu_url(url):
        try:
            parsed = urlparse(url)
        except Exception:
            return False
        if parsed.scheme != "https":
            return False
        if parsed.netloc not in {"kitsu.io", "edge.kitsu.io"}:
            return False
        if not parsed.path.startswith("/api/edge/"):
            return False
        return True

    @staticmethod
    def _is_allowed_rss_url(url):
        try:
            parsed = urlparse(url)
        except Exception:
            return False
        if parsed.scheme != "https":
            return False
        if parsed.netloc != "nyaa.si":
            return False
        return True

    @staticmethod
    def _normalize_kitsu_title(value):
        if not value:
            return ''
        value = value.casefold()
        # Replace bracket-like punctuation (ASCII + common CJK brackets) with spaces.
        value = re.sub(
            r'[\[\]\(\)\{\}<>【】「」『』《》〈〉]',
            ' ',
            value,
        )
        value = re.sub(r'[\W_]+', '', value, flags=re.UNICODE)
        return value

    @staticmethod
    def _normalize_rss_title(value):
        if not value:
            return ''
        value = value.casefold()
        # Remove common tag blocks like [SubsPlease] or (1080p)
        value = re.sub(r'\s?[\[\(\{<](.*?)[\]\)\}>]\s?', ' ', value)
        value = re.sub(r'[\W_]+', '', value, flags=re.UNICODE)
        return value

    @staticmethod
    def _extract_base_and_season(normalized_title):
        """
        Returns (base, season_no|None) from a normalized (no spaces/punct) title.
        Examples:
          oshinokoseason3 -> (oshinoko, 3)
          oshinoko3rdseason -> (oshinoko, 3)
          推しの子第3期 -> (推しの子, 3)
        """
        if not normalized_title:
            return '', None

        season_no = None

        m = re.search(r'season(\d{1,2})', normalized_title)
        if m:
            season_no = int(m.group(1))
        else:
            m = re.search(r'第(\d{1,2})期', normalized_title)
            if m:
                season_no = int(m.group(1))
            else:
                m = re.search(r'(\d{1,2})(st|nd|rd|th)season', normalized_title)
                if m:
                    season_no = int(m.group(1))
                else:
                    m = re.search(r'\bs(\d{1,2})\b', normalized_title)
                    if m:
                        season_no = int(m.group(1))

        base = normalized_title
        base = re.sub(r'(season\d{1,2}|\d{1,2}(st|nd|rd|th)season|第\d{1,2}期)', '', base)
        base = re.sub(r'(season|cour|part|movie|special|tv|theanimation)', '', base)
        base = base.strip()
        return base, season_no

    @staticmethod
    def _season_marker_present(normalized_rss_title, season_no):
        if not season_no:
            return True
        markers = [
            f"season{season_no}",
            f"{season_no}stseason",
            f"{season_no}ndseason",
            f"{season_no}rdseason",
            f"{season_no}thseason",
            f"s{season_no:02d}",
            f"s{season_no}",
        ]
        return any(m in normalized_rss_title for m in markers)

    @staticmethod
    def _season_marker_present_loose(raw_title, season_no):
        """
        Same as _season_marker_present but works on raw title and detects variants like:
        '3rd season', 'season 3', 's03', etc.
        """
        if not season_no:
            return True
        t = (raw_title or "").casefold()
        # Strip tag blocks to avoid false positives from groups/resolutions.
        t = re.sub(r'\s?[\[\(\{<](.*?)[\]\)\}>]\s?', ' ', t)
        return bool(
            re.search(rf'\bseason\s*0*{season_no}\b', t)
            or re.search(rf'\b0*{season_no}(st|nd|rd|th)\s*season\b', t)
            or re.search(rf'\bs0*{season_no}\b', t)
        )

    @staticmethod
    def _title_has_episode(raw_title, episode_no, season_no=None):
        """
        Tries to detect episode patterns without being confused by 1080p/720p etc.
        """
        if not raw_title:
            return False
        t = raw_title.casefold()
        # Remove common tag blocks.
        t = re.sub(r'\s?[\[\(\{<](.*?)[\]\)\}>]\s?', ' ', t)

        # SxxEyy / SxEyy
        m = re.search(r'\bs(?P<s>\d{1,2})\s*e(?P<e>\d{1,3})\b', t)
        if m:
            s = int(m.group('s'))
            e = int(m.group('e'))
            if season_no and s != season_no:
                return False
            # If the release is explicitly tagged as a later season but we don't know the season,
            # avoid matching it to a base-series entry (reduces wrong-season downloads).
            if season_no is None and s > 1:
                return False
            return e == episode_no

        # Ep 01 / Episode 01 / E01
        if re.search(rf'\b(?:ep|episode|e)\s*0*{episode_no}\b', t):
            return True

        # " - 01"
        if re.search(rf'\b-\s*0*{episode_no}\b', t):
            return True

        return False

    def _get_json_with_retries(self, url):
        if not self._is_allowed_kitsu_url(url):
            raise Exception(f"Blocked non-Kitsu URL: {url}")

        last_exc = None
        for _ in range(8):
            try:
                res = self.session.get(url, timeout=30, allow_redirects=False)
                if res.status_code == 200:
                    return res.json()
                if res.status_code == 429:
                    retry_after = res.headers.get("Retry-After")
                    try:
                        sleep(int(retry_after))
                    except Exception:
                        sleep(5)
                    continue
                sleep(2)
            except Exception as e:
                last_exc = e
                sleep(2)
        raise Exception(f"Failed to fetch {url}: {last_exc}")

    def _fetch_rss_entries(self, url):
        if not self._is_allowed_rss_url(url):
            return []
        try:
            res = self.session.get(
                url,
                timeout=30,
                allow_redirects=False,
                headers={"User-Agent": "anime_downloader/1.0", "Accept": "application/rss+xml, application/xml"},
            )
            if res.status_code != 200:
                raise RuntimeError(f"RSS returned HTTP {res.status_code}; stopping this entry")
            if len(res.content) > 2_000_000:
                return []
            parsed = feedparser.parse(res.content)
            return parsed.get("entries") or []
        except requests.RequestException as error:
            raise RuntimeError("RSS request failed; stopping this entry") from error

    def _rss_find_entries_by_titles(self, titles):
        entries = []
        if not titles:
            return entries

        rss_cache = {}
        for title in titles:
            if not isinstance(title, str) or not title.strip():
                continue
            def get_rss_for_query(query):
                rss_feed_url = LibraryEntry.RSS_FEED_URL.format(urllib.parse.quote(query))
                if rss_feed_url in rss_cache:
                    return rss_cache[rss_feed_url]
                print("Fetching rss feed {} ".format(rss_feed_url))
                rss_cache[rss_feed_url] = self._fetch_rss_entries(rss_feed_url)
                return rss_cache[rss_feed_url]

            rss_raw_entries = get_rss_for_query(title)
            if not rss_raw_entries:
                continue

            normalized_kitsu_title = self._normalize_kitsu_title(title)
            base_title, season_no = self._extract_base_and_season(normalized_kitsu_title)
            if not (base_title or normalized_kitsu_title):
                continue

            episode_count = self.anime.episode_count  # episode_count can be null in API
            if episode_count is None:
                episode_count = self.progress + 1

            latest_found_episode = self.progress
            if not self.anime.is_movie:
                for candidate in rss_raw_entries:
                    normalized_candidate = self._normalize_rss_title(candidate.title)
                    if (base_title or normalized_kitsu_title) not in normalized_candidate:
                        continue
                    if season_no and season_no > 1 and not (
                            self._season_marker_present(normalized_candidate, season_no)
                            or self._season_marker_present_loose(candidate.title, season_no)):
                        continue
                    for candidate_episode in range(self.progress + 1, episode_count + 1):
                        if self._title_has_episode(candidate.title, candidate_episode, season_no):
                            latest_found_episode = max(latest_found_episode, candidate_episode)
                episode_count = latest_found_episode

            for episode_no in range(self.progress + 1, episode_count + 1):
                episode_entries = []
                title_token = base_title or normalized_kitsu_title
                regex = '.*{}.*'.format(title_token)

                def collect_episode_entries(candidate_entries):
                    for rss_raw_entry in candidate_entries:
                        cleaned_rss_title = self._normalize_rss_title(rss_raw_entry.title)

                        if base_title and base_title not in cleaned_rss_title:
                            continue

                        strict_season = season_no and season_no > 1
                        if strict_season:
                            # Require an explicit season marker either in normalized title or raw title.
                            if not (
                                    self._season_marker_present(cleaned_rss_title, season_no)
                                    or self._season_marker_present_loose(rss_raw_entry.title, season_no)
                            ):
                                continue

                        if not self.anime.is_movie and not self._title_has_episode(
                                rss_raw_entry.title, episode_no, season_no=season_no
                        ):
                            continue

                        if re.search(regex, cleaned_rss_title):
                            print('Found a match for anime pattern "{}": "{}", no: {}, "{}" seeds'.format(
                                regex, title, episode_no, rss_raw_entry.title
                            ))
                            episode_entries.append(RSSEntry(rss_raw_entry))

                # First, scan the base query feed (usually contains the newest releases).
                collect_episode_entries(rss_raw_entries)

                # If older episodes are missing, Nyaa RSS may not include them in the base feed.
                # Fallback to episode-specific queries to pull older items back into the result window.
                if not episode_entries and not self.anime.is_movie:
                    # Keep this short to avoid excessive requests: Nyaa RSS typically needs only
                    # the episode number appended to bring older releases into the feed window.
                    fallback_queries = [f"{title} {episode_no:02d}", f"{title} {episode_no}"]
                    if season_no:
                        fallback_queries.extend(
                            [
                                f"{title} S{season_no:02d}E{episode_no:02d}",
                                f"{title} S{season_no}E{episode_no:02d}",
                                f"{title} E{episode_no:02d}",
                                f"{title} EP{episode_no:02d}",
                            ]
                        )
                    for q in fallback_queries:
                        collect_episode_entries(get_rss_for_query(q))
                        if episode_entries:
                            break

                if episode_entries:
                    episode_entries.sort()
                    entries.append(episode_entries[0])
                else:
                    # Don't stop on the first gap: releases sometimes skip/rename early episodes,
                    # use different numbering, or have specials; continue searching higher numbers.
                    continue

            if entries:
                # don't check other titles if one resulted in valid entries
                break

        return entries
