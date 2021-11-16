import pytest
from unittest.mock import Mock


@pytest.fixture
def anime_json():
    return {
        'id': 1,
        'attributes': {
            'titles': {},
            'canonicalTitle': '',
            'abbreviatedTitles': [],
            'episodeCount': 0,
            'subtype': 'movie',
            'status': 'current'
        }
    }


@pytest.fixture
def config_json():
    return {
        'transmission_user': 'transmission_user1',
        'server': 'server1',
        'port': 1111,
        'kitsu_user': 'kitsu_user1',
        'transsmision_password': 'password1'
    }


@pytest.fixture
def mock_config():
    m = Mock()
    m.get_kitsu_username.return_value = 'kitsu_user1'
    m.get_transmission_password.return_value = 'password1'
    m.get_transmission_username.return_value = 'transmission_user1'
    m.get_transmission_server.return_value = 'server1'
    m.get_transmission_port.return_value = 1111
    return m


@pytest.fixture
def library_entry_json():
    data = {
        'id': 0,
        'attributes': {
            'progress': 0,
            'status': 'current'
        },
        'relationships': {
            'anime': {
                'links': {
                    'related': 'http://test.com'
                }
            }
        }
    }
    yield data
