import re

from docx.text.paragraph import Paragraph
from docx.text.run import Run


class Song:
    def __init__(self, title):
        self.title: str = title
        self.text: list[str] = list()
        self.chords: list[list[str]] = list()
        self.repetitions: list[str] = list()
        self.authors = str()
        self.has_repetitions = False
        self.chord_columns = 0

    def __str__(self):
        chord_position = max(map(len, self.text)) + 4

        s = self.title.upper() + "\n"
        for text, chords, repetition in zip(self.text, self.chords, self.repetitions):
            s += "\n" + text.ljust(chord_position) + chords[0]
        return s

    def trim(self):
        final_text = list()
        final_chords = list()

        previous_text: str = "text"
        previous_chords: str = "chords"
        previous_ident: int = -1
        for t, c in zip(self.text, self.chords):
            if len(previous_text.strip()) > 0 or len(previous_chords.strip()) > 0 or len(t.strip()) > 0 or len(
                    c[0].strip()) > 0:
                current_ident = get_ident(t)
                if 0 <= previous_ident != current_ident >= 0:
                    final_text.append(str())
                    final_chords.append(str())
                previous_ident = current_ident
                text = t.replace("\t", "&emsp;&emsp;")
                final_text.append(text)
                chords_split = c[0].strip().split("\t")
                split_chords = list()
                for chord in chords_split:
                    split_chords.append(chord.replace("</i><i>", "").replace("</i> <i>", " ")
                                        .replace("</u><u>", "").replace("</u> <u>", " ")
                                        .replace("</sub><sub>", "").replace("</sub> <sub>", " ")
                                        .replace("</sup><sup>", "").replace("</sup> <sup>", " ")
                                        .replace("</b><b>", "").replace("</b> <b>", " ")
                                        .replace("</b><b class=\"chord\">", "").replace("</b> <b class=\"chord\">", " ")
                                        )

                if len(split_chords) > 0 and (split_chords[0].startswith("<b class=\"chord\">|") or
                                              split_chords[0].startswith("<i><b class=\"chord\">|")):
                    self.repetitions.append(split_chords[0].replace(" class=\"chord\"", "").strip())
                    self.has_repetitions = True
                    if len(split_chords) > 1:
                        final_chords.append(get_chords_without_tune_as_chord(split_chords[1:]))
                    else:
                        final_chords.append([str()])
                else:
                    self.repetitions.append(str())
                    final_chords.append(get_chords_without_tune_as_chord(split_chords))

                self.chord_columns = max(len(final_chords[-1]), self.chord_columns)

            previous_text = t
            previous_chords = c[0]
        self.text = final_text
        self.chords = final_chords


def get_songs(pars: list[Paragraph]) -> list[Song]:
    songs: list[Song] = list()

    for par in pars:
        if par.style.name == "Heading 2" and len(par.text.strip()) > 0:
            song = Song(par.text.strip())
            songs.append(song)
        elif len(songs) > 0:
            current_song = songs[-1]
            ident = par.paragraph_format.left_indent \
                if par.paragraph_format.left_indent is not None else par.paragraph_format.first_line_indent
            text, chords = __get_paragraph_from_runs(par.runs, ident)

            current_song.text.extend(text)
            current_song.chords.extend([[c] for c in chords])

    for s in songs:
        s.trim()

    return songs


def get_text_without_classes(string: str):
    result = str(string)
    while True:
        begin = result.find("<")
        end = result.find(">") + 1
        if begin == -1 or end == -1:
            result = re.sub(r'[0-9]+\.', '', result)
            return result.replace("&nbsp;", "").replace("\n", " ").replace("&iuml;", "ï").replace("&oslash;", "ø").strip()
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


def add_authors(songs: list[Song], authors: dict):
    for song in songs:
        song.authors = authors.get(song.title, str())


def __get_line_text(line: str) -> str:
    split = line.strip().split("\t")
    if len(split) == 0:
        return str()
    else:
        return __get_line_begin_tabs(line) + split[0]


def __get_line_begin_tabs(line: str) -> str:
    tabs = str()
    for c in line:
        if c == '\t':
            tabs += '\t'
        else:
            return tabs
    return tabs


def __get_paragraph_from_runs(runs: list[Run], ident) -> tuple[list[str], list[str]]:
    text: list[str] = list()
    chords: list[str] = list()

    current_type = TextType.TEXT

    text.append(str())
    chords.append(str())

    for run in runs:
        if current_type == TextType.TEXT:
            if run.text.startswith("\t"):
                # nie jest to pierwszy znak linii i tabulatory już były
                if len(text) > 0 and len(text[-1]) > 0 and not text[-1].endswith('\t'):
                    if run.bold:
                        current_type = TextType.CHORD
                        run.text = run.text[1:]
                    else:
                        current_type = TextType.NONE

            elif run.bold and not len(run.text.strip()) == 0:
                current_type = TextType.CHORD

            elif run.text.startswith("\n"):
                newlines = __get_newlines_number(run.text)
                text.extend([str() for _ in range(newlines)])
                chords.extend([str() for _ in range(newlines)])
                run.text = run.text[newlines:]

        elif current_type == TextType.CHORD:
            if run.text.startswith("\n"):
                current_type = TextType.TEXT
                run.text = run.text[1:]
                text.append(str())
                chords.append(str())
        else:
            if run.text.startswith("\n"):
                current_type = TextType.TEXT
                run.text = run.text[1:]
                text.append(str())
                chords.append(str())
            elif run.bold and not len(run.text.strip()) == 0:
                current_type = TextType.CHORD

        if current_type == TextType.TEXT:
            text[-1] += __get_html_formatted_text(run)
        elif current_type == TextType.CHORD:
            chords[-1] += __get_html_formatted_text(run, True)

    if ident is not None:
        idents = int((ident / 265430.0) + 0.9)
        for i, line in enumerate(text):
            text[i] = "\t" * idents + line

    return text, chords


def __get_html_formatted_text(run: Run, chords=False) -> str:
    begin = str()
    end = str()

    if len(run.text.strip()) == 0:
        return run.text

    if run.italic:
        begin += "<i>"
        end = "</i>" + end
    if run.underline:
        begin += "<u>"
        end = "</u>" + end
    if run.font.subscript:
        begin += "<sub>"
        end = "</sub>" + end
    if run.font.superscript:
        begin += "<sup>"
        end = "</sup>" + end
    if run.font.strike:
        begin += "<s>"
        end = "</s>" + end
    if run.bold:
        if chords:
            begin += "<b class=\"chord\">"
        else:
            begin += "<b>"
        end = "</b>" + end

    stripped = run.text.strip()
    stripped_origin = stripped
    stripped_pos = run.text.find(stripped)
    stripped = stripped.replace(">", "&gt;")
    stripped = stripped.replace("<", "&lt;")

    return run.text[:stripped_pos] + begin + stripped + end + \
           run.text[stripped_pos + len(stripped_origin):]


def __get_newlines_number(line: str):
    number = 0
    for c in line:
        if c == '\n':
            number += 1
        else:
            return number
    return number


def get_ident(line: str):
    if len(line.strip()) == 0:
        return -1
    ident = 0
    for char in line:
        if char == "\t":
            ident += 1
        else:
            return ident


def get_chords_without_tune_as_chord(chords: list[str]):
    res = list()
    for chord in chords:
        if chord.strip().startswith("<i><b class=\"chord\">("):
            split = chord.split(")", 1)
            split[0] = split[0].replace(" class=\"chord\"", "")
            res.append(")".join(split))
        else:
            res.append(chord)
    return res


class TextType:
    TEXT = 0
    CHORD = 1
    NONE = 2
    REPEAT = 3
