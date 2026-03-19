import argparse
import os
import getpass
import keyring


class Configuration:
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--server', type=str)
        parser.add_argument('--port', type=int)
        parser.add_argument('--kitsu_user', type=str)
        parser.add_argument('--transmission_user', type=str)
        parser.add_argument('--qbittorrent_host', type=str)
        parser.add_argument('--qbittorrent_port', type=int)
        parser.add_argument('--qbittorrent_user', type=str)
        parser.add_argument('--qbittorrent_password', type=str)
        parser.add_argument('--torrent_client', type=str, choices=['transmission', 'qbittorrent'], default='qbittorrent')
        args = parser.parse_args()

        self.transmission_user = args.transmission_user or os.environ.get("TRANSMISSION_USER")
        self.server = args.server or os.environ.get("TRANSMISSION_HOST")
        self.port = args.port or (int(os.environ["TRANSMISSION_PORT"]) if os.environ.get("TRANSMISSION_PORT") else None)
        self.kitsu_user = args.kitsu_user or os.environ.get("KITSU_USER")
        self.qbittorrent_host = args.qbittorrent_host or os.environ.get("QBITTORRENT_HOST")
        self.qbittorrent_port = args.qbittorrent_port or (int(os.environ["QBITTORRENT_PORT"]) if os.environ.get("QBITTORRENT_PORT") else None)
        self.qbittorrent_user = args.qbittorrent_user or os.environ.get("QBITTORRENT_USER")
        # Prefer env var / prompt over CLI arg (CLI args leak via shell history & process list).
        self.qbittorrent_password = (
            os.environ.get("QBITTORRENT_PASSWORD")
            or args.qbittorrent_password
        )
        self.torrent_client = args.torrent_client

        # Set keyring backend explicitly for Windows
        try:
            import keyring.backends.Windows
            keyring.set_keyring(keyring.backends.Windows.WinVaultKeyring())
        except Exception:
            # Avoid forcing insecure plaintext keyring fallback.
            pass

    def get_transmission_password(self):
        transmission_password = None
        try:
            transmission_password = keyring.get_password('anime_downloader', self.transmission_user)
        except Exception:
            transmission_password = None

        if not transmission_password:
            transmission_password = getpass.getpass(prompt='Enter transmission password: ', stream=None).strip()
            if transmission_password:
                try:
                    keyring.set_password('anime_downloader', self.transmission_user, transmission_password)
                except Exception:
                    pass

        return transmission_password

    def get_transmission_username(self):
        return self.transmission_user

    def get_transmission_server(self):
        return self.server

    def get_transmission_port(self):
        return self.port

    def get_kitsu_username(self):
        return self.kitsu_user

    def get_qbittorrent_host(self):
        return self.qbittorrent_host

    def get_qbittorrent_port(self):
        return self.qbittorrent_port

    def get_qbittorrent_user(self):
        return self.qbittorrent_user

    def get_qbittorrent_password(self):
        if not self.qbittorrent_password:
            self.qbittorrent_password = getpass.getpass(prompt='Enter qBittorrent password: ', stream=None).strip()
        return self.qbittorrent_password

    def get_torrent_client(self):
        return self.torrent_client
