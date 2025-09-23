# Project description

Python project allowing to download latest anime episodes releases according to user's Kitsu library.
It's checking "Currently watching" and "Planned to watched" titles and verifying if new, english-translated episodes are present in provided RSS feed.
If yes, it's choosing best quality for episode and starting download with Transmission or qBittorrent server app (selectable).

## Project files
- __Main__ -  Main file starting app, loading config class
- __Library__ - Fetches user's library from Kitsu API. Contains also method for downloading found episodes.
- __LibraryEntry__ - Looks for titles in RSS feed matching user's Kitsu library titles.
- __Anime__ - Single Anime from Kitsu Library API. Responsible for getting all available titles for released anime.
- __RSSEntry__ - Class based on nyaa.si RSS. Assigns particular resolutions to quality and creates a magnet link for given hash. 
- __Configuration__ - initiates reading arguments during app launch. Adds password for transmission app to windows password manager.

## Running

### Transmission example
python main.py --transmission_user=transmission --server=localhost --port=9091 --kitsu_user=eranea --torrent_client=transmission

### qBittorrent example
python main.py --qbittorrent_host=localhost --qbittorrent_port=8080 --qbittorrent_user=qbt_user --qbittorrent_password=qbt_pass --kitsu_user=eranea --torrent_client=qbittorrent