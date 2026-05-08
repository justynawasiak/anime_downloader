class Anime:

    def __init__(self, json):
        self.id = json['id']
        attribs = json['attributes']
        self.titles = attribs.get('titles')
        self.canonical_title = attribs.get('canonicalTitle')
        self.abbreviated_titles = attribs.get('abbreviatedTitles')
        self.episode_count = attribs.get('episodeCount')
        self.is_movie = (attribs.get('subtype') or '').lower() == 'movie'
        self.status = (attribs.get('status') or '').lower()
        self.unreleased = self.status == 'unreleased'

        print("Anime: id {}, released: {}, titles ({})".format(self.id, not self.unreleased, '; '.join(self.get_titles())))

    def get_titles(self):
        titles = []
        if self.titles:
            titles.extend(self.titles.values())
        if self.abbreviated_titles:
            titles.extend(self.abbreviated_titles)
        if self.canonical_title:
            titles.append(self.canonical_title)

        seen = set()
        seen_add = seen.add
        filtered = []
        for t in titles:
            if not isinstance(t, str):
                continue
            t = t.strip()
            if not t:
                continue
            # Avoid ultra-short titles which create very broad RSS matches.
            if len(t) < 2:
                continue
            if t in seen or seen_add(t):
                continue
            filtered.append(t)
        return filtered
