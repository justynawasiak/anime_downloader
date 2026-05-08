import sys
from time import sleep
from urllib.parse import urlparse

import requests
import transmissionrpc
import qbittorrentapi
from libraryEntry import LibraryEntry


class Library:
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/vnd.api+json",
                "User-Agent": "anime_downloader/1.0 (+https://kitsu.io)",
            }
        )
        self.LIBRARY_ENTRIES_URL = 'https://kitsu.io/api/edge/users/{}/library-entries?page%5Blimit%5D=500'
        self.user_id = self.get_user_id(config.get_kitsu_username())
        self.entries = []

        results = self.download_library()
        print('Found {} items in library'.format(len(results)))

        for json_entry in results:
            try:
                try:
                    self.entries.append(LibraryEntry(json_entry, session=self.session))
                except TypeError as e:
                    # Backwards compatibility if LibraryEntry signature doesn't accept `session`.
                    if "unexpected keyword argument 'session'" in str(e):
                        self.entries.append(LibraryEntry(json_entry))
                    else:
                        raise
                # if json_entry['id'] in ('104297520'): # for 1 anime only
                #    self.entries.append(LibraryEntry(json_entry))
            except Exception as e:
                print(f"Skipping entry: {e}")

    @staticmethod
    def _is_allowed_kitsu_url(url):
        try:
            parsed = urlparse(url)
        except Exception:
            return False
        if parsed.scheme != "https":
            return False
        if parsed.netloc not in {"kitsu.io", "edge.kitsu.io"}:
            return False
        if not parsed.path.startswith("/api/edge/"):
            return False
        return True

    def get_user_id(self, username):
        try:
            response_user_id = self.session.get(
                'https://kitsu.io/api/edge/users?filter[slug]={}'.format(username),
                timeout=20,
                allow_redirects=False,
            )
            response_user_id.raise_for_status()
            data = response_user_id.json().get('data') or []
            if not data:
                sys.exit(f'Kitsu user not found: {username}')
            return data[0]['id']
        except Exception as e:
            print(e)

    def download_library(self):
        results = []
        current_url = self.LIBRARY_ENTRIES_URL.format(self.user_id)
        if not self._is_allowed_kitsu_url(current_url):
            sys.exit("Invalid Kitsu URL")

        while current_url:
            for i in range(10):
                res = self.session.get(current_url, timeout=30, allow_redirects=False)
                if res.status_code == 200:
                    break
                if res.status_code == 429:
                    retry_after = res.headers.get("Retry-After")
                    try:
                        sleep(int(retry_after))
                    except Exception:
                        sleep(5)
                    continue
                sleep(2)

            if res.status_code != 200:
                sys.exit(f"Api is unresponsive, try again later")

            response = res.json()

            results.extend(response['data'])
            if 'links' in response and 'next' in response['links']:
                next_url = response['links']['next']
                if not next_url:
                    break
                if not self._is_allowed_kitsu_url(next_url):
                    sys.exit("Invalid Kitsu pagination URL")
                current_url = next_url
            else:
                break
        return results

    def download_found_episode(self):
        client_type = self.config.get_torrent_client()
        if client_type == 'transmission':
            tc = transmissionrpc.Client(
                self.config.get_transmission_server(),
                self.config.get_transmission_port(),
                self.config.get_transmission_username(),
                self.config.get_transmission_password()
            )
            for entry in self.entries:
                if getattr(entry, "status", "").lower() not in {"current", "planned"}:
                    continue
                if entry.rss_entries:
                    for episode in entry.rss_entries:
                        try:
                            tc.add_torrent(episode.get_magnet_link())
                            print("Magnet link added to transmission (entry id={}, status={}): {}, {}, {}".format(
                                getattr(entry, "id", "?"),
                                getattr(entry, "status", "?"),
                                episode.get_rss_title(),
                                episode.get_magnet_link(),
                                episode.get_rss_seeders()))
                            print("  matched anime: id={}, title={}".format(
                                getattr(getattr(entry, "anime", None), "id", "?"),
                                getattr(getattr(entry, "anime", None), "canonical_title", "?"),
                            ))
                        except:
                            print("Duplicated torrent, ignoring.")
        elif client_type == 'qbittorrent':
            qbt_client = qbittorrentapi.Client(
                host=self.config.get_qbittorrent_host(),
                port=self.config.get_qbittorrent_port(),
                username=self.config.get_qbittorrent_user(),
                password=self.config.get_qbittorrent_password()
            )
            try:
                qbt_client.auth_log_in()
            except qbittorrentapi.LoginFailed as e:
                print(f"qBittorrent login failed: {e}")
                return
            for entry in self.entries:
                if getattr(entry, "status", "").lower() not in {"current", "planned"}:
                    continue
                if entry.rss_entries:
                    for episode in entry.rss_entries:
                        try:
                            qbt_client.torrents_add(urls=episode.get_magnet_link())
                            print("Magnet link added to qBittorrent (entry id={}, status={}): {}, {}, {}".format(
                                getattr(entry, "id", "?"),
                                getattr(entry, "status", "?"),
                                episode.get_rss_title(),
                                episode.get_magnet_link(),
                                episode.get_rss_seeders()))
                            print("  matched anime: id={}, title={}".format(
                                getattr(getattr(entry, "anime", None), "id", "?"),
                                getattr(getattr(entry, "anime", None), "canonical_title", "?"),
                            ))
                        except Exception as e:
                            print(f"Error adding torrent to qBittorrent: {e}")
