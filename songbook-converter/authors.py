import re
from typing import Optional

from song_types import IAuthor


def get_text_without_classes(string: str):
    result = str(string)
    while True:
        begin = result.find("<")
        end = result.find(">") + 1
        if begin == -1 or end == -1:
            result = re.sub(r'[0-9]+\.', '', result)
            return result.replace("&nbsp;", "").replace("\n", " ").replace("&iuml;", "ï").replace("&oslash;",
                                                                                                  "ø").strip()
        result = result[:begin] + result[end:]


def get_authors_without_classes(string: str) -> list[str]:
    single_authors = re.split(r"</p>", string)
    authors_list = [re.sub(r' +', ' ', get_text_without_classes(author)) for author in single_authors]
    return [author for author in authors_list if len(author) > 0]


def get_authors(path: str) -> dict[str, list[str]]:
    with open(path, "r", encoding="windows-1250") as file:
        html = file.read()
        headers = list()
        while True:
            start = html.find("<h2")
            if start == -1: break
            end = html.find("</h2>")
            headers.append(html[start:end + 5])
            html = html[end + 5:]

        authors = dict()
        for header in headers:
            begin = header.rfind("</v:shape>")
            if begin > -1:
                begin += len("</v:shape>")
            else:
                begin = 0
            title = get_text_without_classes(header[begin:-5])

            begin = header.find("<v:textbox")
            end = header.find("</v:textbox>")
            if begin < 0:
                authors[title] = None
            else:
                authors[title] = get_authors_without_classes(header[begin:end + len("</v:textbox>")])

    return authors


def parse_single_author(author: str) -> IAuthor:
    author = re.split(r"\.? ", author, 1)
    a = IAuthor(author[0])
    if len(author) > 1:
        a.lastName = author[1]
    return a


def parse_author(author: str) -> list[IAuthor]:
    authors = re.split("(?: i )|(?:, )", author)
    authors = [parse_single_author(a) for a in authors]
    if len(authors) >= 2 and authors[0].lastName is None and len(authors[0].name) == 1 and \
            authors[1].lastName is not None:
        authors[0].lastName = authors[1].lastName
    return authors


def parse_authors(authors: list[str]) -> tuple[
    Optional[list[IAuthor]], Optional[list[IAuthor]], Optional[list[IAuthor]]]:
    performance: Optional[list[IAuthor]] = []
    lyrics: Optional[list[IAuthor]] = []
    music: Optional[list[IAuthor]] = []
    for author in authors:
        if author.startswith("sł."):
            if author.startswith("sł. i muz."):
                author = author[10:].strip()
                music.extend(parse_author(author))
            else:
                author = author[3:].strip()
            lyrics.extend(parse_author(author))
        elif author.startswith("muz."):
            music.extend(parse_author(author[4:].strip()))
        else:
            performance.extend(parse_author(author))
    if len(performance) == 0:
        performance = None
    if len(lyrics) == 0:
        lyrics = None
    if len(music) == 0:
        music = None
    if performance is not None and performance[0].name == "Jacek" and performance[0].lastName == "Kaczmarski":
        if lyrics is None:
            lyrics[0] = performance[0]
        if music is None:
            music[0] = performance[0]
    return performance, lyrics, music
