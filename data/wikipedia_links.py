import json
from typing import Optional

import requests


with open('data/authors.json', encoding='utf-8') as file:
    authors = json.load(file)

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


def resolve_author_url(author: dict) -> str | None:
    url = wikipedia_search_url + author["name"] + '+' + author["lastName"]
    wiki = resolve_wikipedia_url(url)
    if "?search" in wiki:
        wiki = resolve_wikipedia_url(url.replace("pl", "en", 1))
    return wiki if "?search" not in wiki else url


for author in authors:
    wiki = resolve_author_url(author)
    if wiki:
        author["url"] = wiki

    print(author)
