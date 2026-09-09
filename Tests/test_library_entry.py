from unittest import mock

import requests_mock
import pytest
from types import SimpleNamespace

import rssEntry
from libraryEntry import LibraryEntry


def test_search_fills_older_gap_without_querying_future_episodes():
    entry = LibraryEntry.__new__(LibraryEntry)
    entry.progress = 0
    entry.anime = SimpleNamespace(episode_count=12, is_movie=False)

    def release(episode):
        return SimpleNamespace(title=f'Example S02E{episode:02d}', link='unused',
                               nyaa_infohash=str(episode), nyaa_seeders='2')

    latest = release(2)
    older = release(1)
    with mock.patch.object(entry, '_fetch_rss_entries', side_effect=[[latest], [older]]) as fetch:
        found = entry._rss_find_entries_by_titles(['Example Season 2'])
    assert [episode.rss_title for episode in found] == [older.title, latest.title]
    assert fetch.call_count == 2


def test_search_does_not_query_episodes_for_unmatched_feed():
    entry = LibraryEntry.__new__(LibraryEntry)
    entry.progress = 0
    entry.anime = SimpleNamespace(episode_count=24, is_movie=False)
    with mock.patch.object(entry, '_fetch_rss_entries', return_value=[
            SimpleNamespace(title='Unrelated S02E01')]) as fetch:
        assert entry._rss_find_entries_by_titles(['Example Season 2']) == []
    assert fetch.call_count == 1


def test_rss_rate_limit_stops_entry():
    entry = LibraryEntry.__new__(LibraryEntry)
    entry.session = mock.Mock()
    entry.session.get.return_value.status_code = 429
    with pytest.raises(RuntimeError, match='429'):
        entry._fetch_rss_entries('https://nyaa.si/?page=rss')
    assert entry.session.get.call_args.kwargs['allow_redirects'] is False


def test_library_entry(library_entry_json):
    rss_entries = [type('rss_entry', (object,), {
        'title': 'title1.mkv',
        'link': 'rss_link',
        'nyaa_infohash': 'nyaa_infohash',
        'nyaa_seeders': '2'
    })]

    with requests_mock.Mocker() as mr:
        anime_data = {
            'data': {
                'id': 1,
                'attributes': {
                    'titles': {0: 'title1'},
                    'canonicalTitle': 'title2',
                    'abbreviatedTitles': ['title3'],
                    'episodeCount': 1,
                    'subtype': 'movie',
                    'status': 'current'
                }
            }
        }
        mr.get("https://kitsu.io/api/edge/anime/1", json=anime_data)

        with mock.patch.object(LibraryEntry, "_fetch_rss_entries", return_value=rss_entries):
            le = LibraryEntry(library_entry_json)

        assert len(le.rss_entries) == 1
        entry = le.rss_entries[0]
        mock_entry = rss_entries[0]
        assert entry.rss_title == mock_entry.title
        assert entry.torrent_link == mock_entry.link
        assert entry.info_hash == mock_entry.nyaa_infohash
        assert entry.seeders == int(mock_entry.nyaa_seeders)
        assert entry.quality == rssEntry.RSSEntry.RESOLUTION_UNKNOWN
