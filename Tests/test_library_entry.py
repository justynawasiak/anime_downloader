from unittest import mock

import requests_mock

import rssEntry
from libraryEntry import LibraryEntry


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
