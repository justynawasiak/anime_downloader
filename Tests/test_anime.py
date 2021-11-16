from anime import Anime


def test_get_empty_titles(anime_json):
    a = Anime(anime_json)
    assert a.get_titles() == []


def test_get_titles(anime_json):
    anime_json['attributes']['titles'][0] = 'title1'
    anime_json['attributes']['abbreviatedTitles'].append('title2')
    anime_json['attributes']['canonicalTitle'] = 'title3'
    b = Anime(anime_json)
    assert b.get_titles() == ['title1', 'title2', 'title3']
