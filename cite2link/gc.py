import requests
from urllib.parse import urlencode

talk_finder_url_template = "https://duckduckgo.com/?{q}&va=j&t=hc&ia=web"


def expand_conf_id(conf_id):
    month = 'april' if conf_id[0].lower() == 'a' else 'october'
    year = int(conf_id[-2:])
    year += 2000 if year < 77 else 1900
    return month, year


def find_talk(conf_id, speaker_surname, keywords):
    month, year = expand_conf_id(conf_id)
    query = urlencode({
        "q": f'site:churchofjesuschrist.org "{month} {year} general conference" {speaker_surname} {keywords}'
    })
    url = talk_finder_url_template.replace("{q}", query)
    resp = requests.get(url)
    return resp.text