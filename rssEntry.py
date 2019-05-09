class RSSEntry:
    RESOLUTION_FULLHD = 0
    RESOLUTION_HD = 1
    RESOLUTION_SD = 2
    RESOLUTION_UNKNOWN = 255

    def __init__(self, rss_raw_entry):
        self.torrent_link = rss_raw_entry.link
        self.info_hash = rss_raw_entry.nyaa_infohash
        self.rss_title = rss_raw_entry.title.lower()
        self.seeders = int(rss_raw_entry.nyaa_seeders)

        if '1080p' in self.rss_title or '1080i' in self.rss_title or 'bdrip' in self.rss_title:
            self.quality = RSSEntry.RESOLUTION_FULLHD
        elif '720p' in self.rss_title or '720i' in self.rss_title:
            self.quality = RSSEntry.RESOLUTION_HD
        elif '480p' in self.rss_title or '360p' in self.rss_title:
            self.quality = RSSEntry.RESOLUTION_SD
        else:
            self.quality = RSSEntry.RESOLUTION_UNKNOWN

    def __lt__(self, other):
        if self.quality == other.quality:
            return self.seeders > other.seeders
        return self.quality < other.quality

    def get_magnet_link(self):
        return 'magnet:?xt=urn:btih:{}'.format(self.info_hash)

    def get_rss_title(self):
        return self.rss_title

    def get_rss_seeders(self):
        return self.seeders