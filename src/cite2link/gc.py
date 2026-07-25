# ~4g46 UNFINISHED + INERT. This General Conference talk finder is not wired
# into the CLI and is not reachable through resolve(); GC-citation parsing is
# opt-in (cite.parse(..., allow_gc=True)). find_talk() only fetches raw search
# HTML — it does not yet extract the canonical talk URL — and has no live test.
# `requests` is an opt-in [gc] extra. See the tick for what remains to finish.
from urllib.parse import urlencode

talk_finder_url_template = "https://duckduckgo.com/?{q}&va=j&t=hc&ia=web"


def expand_conf_id(conf_id):
    month = "april" if conf_id[0].lower() == "a" else "october"
    year = int(conf_id[-2:])
    year += 2000 if year < 77 else 1900
    return month, year


def find_talk(conf_id, speaker_surname, keywords):
    # `requests` is imported lazily so the rest of cite2link stays
    # dependency-free; the General Conference talk finder is an unfinished,
    # opt-in extra (install the `gc` extra to use it).
    import requests

    month, year = expand_conf_id(conf_id)
    query = urlencode(
        {
            "q": f'site:churchofjesuschrist.org "{month} {year} general conference" {speaker_surname} {keywords}'
        }
    )
    url = talk_finder_url_template.replace("{q}", query)
    resp = requests.get(url)
    return resp.text
