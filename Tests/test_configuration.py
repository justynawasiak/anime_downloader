import argparse
import builtins
from unittest import mock
from configuration import Configuration


@mock.patch('argparse.ArgumentParser.parse_args',
            return_value=argparse.Namespace(transmission_user='transmission_user1', server='server1', port=1111, kitsu_user='kitsu_user1'))
def test_basic_config(mock_args, config_json):
    conf = Configuration()
    assert conf.get_transmission_username() == config_json['transmission_user']
    assert conf.get_transmission_server() == config_json['server']
    assert conf.get_transmission_port() == config_json['port']
    assert conf.get_kitsu_username() == config_json['kitsu_user']


@mock.patch('keyring.get_password', return_value='password1')
@mock.patch('argparse.ArgumentParser.parse_args',
            return_value=argparse.Namespace(transmission_user='transmission_user1', server='server1', port=1111, kitsu_user='kitsu_user1'))
def test_get_pass(mock_args, mock_args2):
    conf = Configuration()
    password_to_set = 'password1'
    mock.patch.object(builtins, 'input', lambda _: password_to_set)
    assert conf.get_transmission_password() == password_to_set

