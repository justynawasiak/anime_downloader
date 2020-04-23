class Anime:

    def __init__(self, json):
        self.id = json['id']
        attribs = json['attributes']
        self.titles = attribs['titles']
        self.slug = attribs['slug']
        self.canonical_title = attribs['canonicalTitle']
        self.abbreviated_titles = attribs['abbreviatedTitles']
        self.episode_count = attribs['episodeCount']
        self.is_movie = attribs['subtype'].lower() == 'movie'
        self.unreleased = attribs['status'].lower() == 'unreleased'

        print("Anime: id {}, released: {}, titles ({})".format(self.id, not self.unreleased, '; '.join(self.get_titles())))

    def get_titles(self):
        titles = []
        if not self.unreleased:
            if self.canonical_title: titles.append(self.canonical_title)
            if self.abbreviated_titles: titles.extend(self.abbreviated_titles)
            #if self.titles:
            #    for k, v in self.titles.items():
            #        titles.append(v)
            #if self.slug: titles.append(self.slug)

        seen = set()
        seen_add = seen.add
        return [x for x in titles if not (x in seen or seen_add(x))]