import urllib.parse


class RSSEntry:
    RESOLUTION_FULLHD = 0
    RESOLUTION_HD = 1
    RESOLUTION_SD = 2
    RESOLUTION_UNKNOWN = 255

    def __init__(self, rss_raw_entry):
        self.torrent_link = rss_raw_entry.link
        self.info_hash = rss_raw_entry.nyaa_infohash
        self.rss_title = rss_raw_entry.title
        self.seeders = int(rss_raw_entry.nyaa_seeders)

        rss_title_lower = self.rss_title.lower()

        if '1080p' in rss_title_lower or '1080i' in rss_title_lower or 'bdrip' in rss_title_lower:
            self.quality = RSSEntry.RESOLUTION_FULLHD
        elif '720p' in rss_title_lower or '720i' in rss_title_lower:
            self.quality = RSSEntry.RESOLUTION_HD
        elif '480p' in rss_title_lower or '360p' in rss_title_lower:
            self.quality = RSSEntry.RESOLUTION_SD
        else:
            self.quality = RSSEntry.RESOLUTION_UNKNOWN

    def __lt__(self, other):
        if self.quality == other.quality:
            return self.seeders > other.seeders
        return self.quality < other.quality

    def get_magnet_link(self):
        return 'magnet:?xt=urn:btih:{}&dn={}'.format(self.info_hash, urllib.parse.quote('[anime] {}'.format(self.rss_title)))

    def get_rss_title(self):
        return self.rss_title

    def get_rss_seeders(self):
        return self.seeders