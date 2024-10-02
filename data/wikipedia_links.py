import json
import requests


with open('data/bands.json', encoding='utf-8') as file:
    bands = json.load(file)

wikipedia_search_url = "https://pl.wikipedia.org/?search="


def resolve_wikipedia_url(search_url):
    try:
        response = requests.get(search_url, allow_redirects=True)

        if response.history:
            return response.url
        else:
            return None
    except requests.RequestException as e:
        print(f"Error fetching URL {search_url}: {e}")
        return None


def resolve_band_url(band: dict) -> str | None:
    url = wikipedia_search_url + band["name"]
    wiki = resolve_wikipedia_url(url)
    if "?search" in wiki:
        wiki = resolve_wikipedia_url(url.replace("pl", "en", 1))

    return wiki if "?search" not in wiki else url


print("[")
for band in bands:
    wiki = resolve_band_url(band)
    if wiki:
        band["url"] = wiki

    print(json.dumps(band, ensure_ascii=False) + ",")

print("]")
