import argparse
import getpass
import keyring


class Configuration:
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--transmission_user', type=str)
        parser.add_argument('--server', type=str)
        parser.add_argument('--port', type=int)
        parser.add_argument('--kitsu_user', type=str)
        args = parser.parse_args()

        self.transmission_user = args.transmission_user
        self.server = args.server
        self.port = args.port
        self.kitsu_user = args.kitsu_user

    def get_transmission_password(self):
         transmission_password = keyring.get_password('anime_downloader', self.transmission_user)
         if not transmission_password:
            transmission_password = getpass.getpass(prompt='Enter transmission password: ', stream=None).strip()
            if transmission_password:
                keyring.set_password('anime_downloader', self.transmission_user, transmission_password)
         return transmission_password

    def get_transmission_username(self):
        return self.transmission_user

    def get_transmission_server(self):
        return self.server

    def get_transmission_port(self):
        return self.port

    def get_kitsu_username(self):
        return self.kitsu_user
