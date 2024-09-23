from docx.text.paragraph import Paragraph
from docx.text.run import Run

from authors import parse_authors
from song_types import ILine, ITextRun, ISong, ICategory, IEditorInfo, ISongKey, IKey, INote, IVerse
from str_convert import title_to_unique_name


class Song:
    def __init__(self, title):
        self.title: str = title
        self.lines: list[ILine] = list()
        self.chords: list[list[str]] = list()
        # self.repetitions: list[str] = list()
        self.authors: list[str] = []
        self.chord_columns = 0

    def to_song_data(self) -> ISong:
        verses: list[IVerse] = [IVerse([], 0)]
        for line in self.lines:
            if len(line.text) == 0:
                if len(verses[-1].lines) > 0:
                    verses.append(IVerse([], 0))
            else:
                line.text[0].text, indent = strip_tabs(line.text[0].text)
                if len(verses[-1].lines) == 0:
                    verses[-1].indent = indent
                elif indent != verses[-1].indent:
                    verses.append(IVerse([], indent))
                verses[-1].lines.append(line)

                if line.text[-1].text.endswith("…"):    # szukamy oryginalnej powtarzanej zwrotki
                    for i, verse in enumerate(verses):
                        if i < len(verses) - 1 and verse_starts_with_short_line(verse, line):
                            verses[-1].verseRef = i
                            break
                    verses.append(IVerse([], 0))
        if len(verses[-1].lines) == 0:
            verses.pop()

        song = ISong(title_to_unique_name(self.title), self.title, ICategory("", ""),
                     IEditorInfo("spiewnik-mmakos", 1726832509, True, False),
                     ISongKey(IKey(INote("C"))), verses)
        song.performers, song.lyrics, song.composer = parse_authors(self.authors)
        return song

    def trim(self):
        for line in self.lines:
            line.text = [run for i, run in enumerate(line.text) if (run.text and not run.text.isspace()) or i == 0]
            if len(line.text) == 1 and (not line.text[0].text or line.text[0].text.isspace()):
                line.text = []


def verse_starts_with_short_line(verse: IVerse, short_line: ILine) -> bool:
    line = verse.lines[0]
    if len(line.text) == 0:
        return False
    line_text = "".join(r.text for r in line.text)
    short_line_text = "".join(r.text for r in short_line.text)[:-1]
    return line_text.startswith(short_line_text)


def get_songs(pars: list[Paragraph], authors: dict[str, list[str]]) -> list[ISong]:
    songs: list[Song] = list()

    for par in pars:
        if par.style.name == "Heading 2" and len(par.text.strip()) > 0:
            # if len(songs) >= 3:
            #     break  # TODO na razie tylko 3 pierwsze piosenki
            song = Song(par.text.strip())
            auth = authors.get(song.title)
            if auth is not None:
                song.authors = auth
            songs.append(song)
        elif len(songs) > 0:
            current_song: Song = songs[-1]
            indent = par.paragraph_format.left_indent \
                if par.paragraph_format.left_indent is not None else par.paragraph_format.first_line_indent
            lines = __get_paragraph_from_runs(par.runs, indent)

            current_song.lines.extend(lines)
            # current_song.chords.extend([[c] for c in chords])

    for song in songs:
        song.trim()

    return [song.to_song_data() for song in songs]


def __get_paragraph_from_runs(runs: list[Run], indent: int) -> list[ILine]:
    chords: list[str] = [""]
    lines: list[ILine] = [ILine([])]

    current_type = TextType.TEXT

    for run in runs:
        if current_type == TextType.TEXT:
            if run.text.startswith("\t"):
                # nie jest to pierwszy znak linii i tabulatory już były
                if len(lines[-1].text) > 0 and lines[-1].text[-1].text and lines[-1].text[-1].text.endswith('\t'):
                    if run.bold:
                        current_type = TextType.CHORD
                        run.text = run.text[1:]
                    else:
                        current_type = TextType.NONE

            elif run.bold and not len(run.text.strip()) == 0:
                current_type = TextType.CHORD

            elif run.text.startswith("\n"):
                newlines = __get_newlines_number(run.text)
                lines.extend([ILine([]) for _ in range(newlines)])
                chords.extend([str() for _ in range(newlines)])
                run.text = run.text[newlines:]

        elif current_type == TextType.CHORD:
            if run.text.startswith("\n"):
                current_type = TextType.TEXT
                run.text = run.text[1:]
                lines.append(ILine([]))
                chords.append(str())
        else:
            if run.text.startswith("\n"):
                current_type = TextType.TEXT
                run.text = run.text[1:]
                lines.append(ILine([]))
                chords.append(str())
            elif run.bold and not len(run.text.strip()) == 0:
                current_type = TextType.CHORD

        if current_type == TextType.TEXT:
            run = __get_line_text_run(run)
            if len(lines[-1].text) > 0:
                prev = lines[-1].text[-1]
                if run.bold == prev.bold and run.italic == prev.italic and run.underline == prev.underline:
                    prev.text += run.text
                else:
                    lines[-1].text.append(run)
            else:
                lines[-1].text.append(run)
        elif current_type == TextType.CHORD:
            chords[-1] += __get_html_formatted_text(run, True)

    if indent is not None:
        indents = int((indent / 265430.0) + 0.9)
        for line in lines:
            if len(line.text) > 0 and len(line.text[0].text) > 0:  # TODO czy pierwszy warunek jest potrzebny (czasem się psuje)
                line.text[0].text = "\t" * indents + line.text[0].text

    return lines


def __get_line_text_run(run: Run) -> ITextRun:
    text_run = ITextRun(run.text)

    if len(run.text.strip()) == 0:
        return text_run

    if run.italic:
        text_run.italic = True
    if run.underline:
        text_run.underline = True
    if run.bold:
        text_run.bold = True

    return text_run


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


def strip_tabs(line: str) -> (str, int):
    new_line = line.lstrip("\t")
    return new_line, len(line) - len(new_line)


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
