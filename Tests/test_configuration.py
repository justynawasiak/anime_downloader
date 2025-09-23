import argparse
import builtins
from unittest import mock
from configuration import Configuration



@mock.patch('argparse.ArgumentParser.parse_args',
            return_value=argparse.Namespace(
                transmission_user='transmission_user1', server='server1', port=1111, kitsu_user='kitsu_user1',
                qbittorrent_host='localhost', qbittorrent_port=8080, qbittorrent_user='qbt_user', qbittorrent_password='qbt_pass', torrent_client='qbittorrent'))
def test_basic_config_qbittorrent(mock_args):
    conf = Configuration()
    assert conf.get_transmission_username() == 'transmission_user1'
    assert conf.get_transmission_server() == 'server1'
    assert conf.get_transmission_port() == 1111
    assert conf.get_kitsu_username() == 'kitsu_user1'
    assert conf.get_qbittorrent_host() == 'localhost'
    assert conf.get_qbittorrent_port() == 8080
    assert conf.get_qbittorrent_user() == 'qbt_user'
    assert conf.get_qbittorrent_password() == 'qbt_pass'
    assert conf.get_torrent_client() == 'qbittorrent'


@mock.patch('argparse.ArgumentParser.parse_args',
            return_value=argparse.Namespace(
                transmission_user='transmission_user1', server='server1', port=1111, kitsu_user='kitsu_user1',
                qbittorrent_host=None, qbittorrent_port=None, qbittorrent_user=None, qbittorrent_password=None, torrent_client='transmission'))
def test_basic_config_transmission(mock_args):
    conf = Configuration()
    assert conf.get_torrent_client() == 'transmission'

