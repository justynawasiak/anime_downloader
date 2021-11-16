from unittest import mock

from library import Library
import requests_mock


@mock.patch('libraryEntry.LibraryEntry')
def test_library(mock_library_entry, mock_config):
    with requests_mock.Mocker() as mr:
        kitsu_user_data = {
            'data': [
                {
                    'id': 1
                }
            ]
        }
        kitsu_library_data = {
            'data': [
                {
                    'id': 1,
                    'attributes': {
                        'titles': {0: 'title1'},
                        'canonicalTitle': 'title2',
                        'abbreviatedTitles': ['title3'],
                        'episodeCount': 1,
                        'subtype': 'movie',
                        'status': 'current',
                        'progress': 1
                    }
                }
            ]
        }
        user_id = kitsu_user_data['data'][0]['id']
        mr.get(f"https://kitsu.io/api/edge/users?filter[name]={mock_config.get_kitsu_username()}", json=kitsu_user_data)
        mr.get(f"https://kitsu.io/api/edge/users/{user_id}/library-entries?page%5Blimit%5D=500", json=kitsu_library_data)
        lib = Library(mock_config)
        pass
