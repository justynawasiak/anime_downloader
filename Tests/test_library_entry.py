from unittest import mock

import rssEntry
from libraryEntry import LibraryEntry
import requests_mock


@mock.patch('feedparser.parse', return_value={'entries': [type('rss_entry', (object,), {
    'title': 'title1.mkv',
    'link': 'rss_ink',
    'nyaa_infohash': 'nyaa_unfihash',
    'nyaa_seeders': '2'
})]})
def test_library_entry(feed_parser, library_entry_json):
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
        mr.get("http://test.com", json=anime_data)
        le = LibraryEntry(library_entry_json)
        assert len(le.rss_entries) == 1
        entry = le.rss_entries[0]
        mock_entry = feed_parser.return_value['entries'][0]
        assert entry.rss_title == mock_entry.title
        assert entry.torrent_link == mock_entry.link
        assert entry.info_hash == mock_entry.nyaa_infohash
        assert entry.seeders == int(mock_entry.nyaa_seeders)
        assert entry.quality == rssEntry.RSSEntry.RESOLUTION_UNKNOWN
