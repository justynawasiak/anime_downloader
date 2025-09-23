import argparse
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

        self.transmission_user = args.transmission_user
        self.server = args.server
        self.port = args.port
        self.kitsu_user = args.kitsu_user
        self.qbittorrent_host = args.qbittorrent_host
        self.qbittorrent_port = args.qbittorrent_port
        self.qbittorrent_user = args.qbittorrent_user
        self.qbittorrent_password = args.qbittorrent_password
        self.torrent_client = args.torrent_client

        # Set keyring backend explicitly for Windows
        try:
            import keyring.backends.Windows
            keyring.set_keyring(keyring.backends.Windows.WinVaultKeyring())
        except Exception:
            try:
                import keyrings.alt
                keyring.set_keyring(keyrings.alt.file.PlaintextKeyring())
            except Exception:
                pass

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

    # ...existing code...
        self.torrent_client = args.torrent_client

    def get_qbittorrent_host(self):
        return self.qbittorrent_host

    def get_qbittorrent_port(self):
        return self.qbittorrent_port

    def get_qbittorrent_user(self):
        return self.qbittorrent_user

    def get_qbittorrent_password(self):
        return self.qbittorrent_password

    def get_torrent_client(self):
        return self.torrent_client
