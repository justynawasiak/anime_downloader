import sys
from time import sleep

import requests
import transmissionrpc
from libraryEntry import LibraryEntry


class Library:
    def __init__(self, config):
        self.config = config
        self.LIBRARY_ENTRIES_URL = 'https://kitsu.io/api/edge/users/{}/library-entries?page%5Blimit%5D=500'
        self.user_id = self.get_user_id(config.get_kitsu_username())
        self.entries = []

        results = self.download_library()
        print('Found {} items in library'.format(len(results)))

        for json_entry in results:
            try:
                self.entries.append(LibraryEntry(json_entry))
                #if json_entry['id'] in ('50961939'): #for 1 anime only
                #    self.entries.append(LibraryEntry(json_entry))
            except Exception as e:
                print(e)

    @staticmethod
    def get_user_id(username):
        try:
            response_user_id = requests.get('https://kitsu.io/api/edge/users?filter[slug]={}'.format(username))
            return response_user_id.json()['data'][0]['id']
        except Exception as e:
            print(e)

    def download_library(self):
        results = []
        current_url = self.LIBRARY_ENTRIES_URL.format(self.user_id)

        while current_url:
            for i in range(10):
                res = requests.get(current_url)
                if res.status_code == 200:
                    break
                sleep(2)

            if res.status_code != 200:
                sys.exit(f"Api is unresponsive, try again later")

            response = res.json()

            results.extend(response['data'])
            if 'links' in response and 'next' in response['links']:
                current_url = response['links']['next']
            else:
                break
        return results

    def download_found_episode(self):
        for entry in self.entries:
            if entry.rss_entries:
                for episode in entry.rss_entries:
                    print("Magnet link added to transmission: {}, {}, {}".format(episode.get_rss_title(), episode.get_magnet_link(), episode.get_rss_seeders()))

                    tc = transmissionrpc.Client(self.config.get_transmission_server(), self.config.get_transmission_port(), self.config.get_transmission_username(), self.config.get_transmission_password())
                    tc.add_torrent(episode.get_magnet_link())