import time
from typing import Optional

from docx.text.paragraph import Paragraph
from docx.text.run import Run

from Songbook.str_convert import title_to_unique_name
from songbook_converter.authors import parse_authors
from songbook_converter.song_types import ILine, IChord, IAdditionalSeries, IElement, INote, IChords, IChordSeries, \
    IComplexChord, ITextRun, ISong, ICategory, IEditorInfo, ISongKey, IKey, IVerse, ISongOverview

# STATES
NONE = 0
TEXT = 1
CHORD = 2
BASE = 3
ADDITIONAL = 4
ALTERNATIVE = 5
REPETITION = 7
CHORD_REPETITION = 8  # TODO
KEY = 9
KEY_CHANGE = 10  # ->
COMFORT_KEY = 11
SILENT_CHORD = 12
TAB = 13
ALTERNATIVE_KEY = 14


def is_chord_state(state):
    return state == CHORD or state == ALTERNATIVE or state == SILENT_CHORD


def parse_songs(pars: list[Paragraph], authors: dict[str, list[str]]) -> list[ISong]:
    songs: list[tuple[str, list[Paragraph]]] = list()

    for par in pars:
        if par.style.name == "Heading 2" and len(par.text.strip()) > 0:
            songs.append((par.text.strip(), list()))
        elif len(songs) > 0:
            songs[-1][1].append(par)

    # songs = songs[367:368]     # TODO
    parsed_songs = [parse_song(song[0], song[1], authors) for song in songs]
    for i, parsed in enumerate(parsed_songs):
        next = parsed_songs[(i + 1) % len(parsed_songs)]
        prev = parsed_songs[(i - 1) % len(parsed_songs)]
        parsed.next = ISongOverview(next.id, next.title)
        parsed.previous = ISongOverview(prev.id, prev.title)

    return parsed_songs


def parse_song(title: str, pars: list[Paragraph], authors: dict[str, list[str]]):
    # print(f'---- Parsowanie piosenki: {title}')
    lines = []
    keys = [None, None, None]
    for par in pars:
        try:
            # print(par.text)
            line, ks = parse_paragraph(title, par)
        except Exception as e:
            print(f'Blad krytyczny w piosence {title}')
            raise e
        if all(key is None for key in keys) and any(key is not None for key in ks):
            keys = ks
        lines.extend(line)


    verses = []
    verse = IVerse([], 0)
    for line in lines:
        assert line.text is not None

        if len(line.text) > 0 and (len(line.text) > 1 or not line.text[0].text.isspace()):
            indent = len(line.text[0].text) - len(line.text[0].text.lstrip('\t'))
            if indent != verse.indent:
                if len(verse.lines) > 0:
                    verses.append(verse)
                    verse = IVerse([], indent)
                else:
                    verse.indent = indent

        # trim trailing whitespaces
        while True:
            if len(line.text) > 0 and len(line.text[0].text.strip()) == 0:
                line.text.pop(0)
            else:
                if len(line.text) > 0:
                    line.text[0].text = line.text[0].text.lstrip()
                break
        # trim end whitespaces
        while True:
            if len(line.text) > 0 and len(line.text[-1].text.strip()) == 0:
                line.text.pop()
            else:
                if len(line.text) > 0:
                    line.text[-1].text = line.text[-1].text.rstrip()
                break

        if len(line.text) == 0:
            line.text = None
        if line.text == None and (line.chords is None or len(line.chords.chords) == 0):
            if len(verse.lines) > 0:
                verses.append(verse)
                verse = IVerse([], 0)
        else:
            verse.lines.append(line)

    if len(verse.lines) > 0:
        verses.append(verse)

    for verse in verses:
        if len(verse.lines) == 1 and verse.lines[0].text is not None and verse.lines[0].text[-1].text.endswith("…"):
            for i, v in enumerate(verses):
                if verse_starts_with_short_line(v, verse.lines[0]) and len(v.lines) > 1:
                    verse.verseRef = i
                    break

    song = ISong(title_to_unique_name(title), title, ICategory("", ""),
                 IEditorInfo("spiewnik-mmakos", int(time.time()), True, False), verses)

    for line in lines:
        if line.chords is not None:
            song.key = ISongKey(
                IKey(line.chords.chords[0].chords[0].chord.note, line.chords.chords[0].chords[0].chord.minor))
            break

    if song.key:
        song.key.original = keys[0]
        song.key.comfort = keys[1]
        song.key.maxComfort = keys[2]

    auth = authors.get(song.title)
    if auth is not None:
        song.performers, song.lyrics, song.composer = parse_authors(auth)

    return song


def parse_paragraph(title: str, par: Paragraph) -> tuple[
    list[ILine], tuple[Optional[IKey], Optional[IKey], Optional[IKey]]]:
    state = NONE
    chord_state = NONE
    line = ILine([ITextRun("")])
    lines = []
    original_key: Optional[IKey] = None
    comfort_key: Optional[IKey] = None
    max_comfort_key: Optional[IKey] = None

    indent = par.paragraph_format.left_indent \
        if par.paragraph_format.left_indent is not None else par.paragraph_format.first_line_indent

    for run in par.runs:
        text = run.text
        strip = text.strip()
        # calculate state
        if run.text.startswith('\n'):
            lines.append(line)
            line = ILine([ITextRun("")])
            text = run.text[1:]
            run.text = text
            state = NONE
            chord_state = NONE
        if state == ALTERNATIVE_KEY:
            continue
        if run.text == '\t' or (run.text.startswith('\t') and is_chord_state(state)):
            if line.chords is None and len(line.text) == 1 and len(line.text[0].text) == 0:
                state = TEXT
                line.text[0].text += '\t'
                continue
            if state == TEXT or state == REPETITION:
                state = TAB
            else:
                state = ALTERNATIVE_KEY
        elif not run.bold:
            if state == NONE or state == TEXT or state == TAB:
                state = TEXT
            else:
                if not run.text.isspace():
                    print(
                        f"Niespodziewany stan dla run: {run.text}, par: {par.text}, song: {title}, brak pogrubienia po stanie innym niż NONE lub TEXT - być może komentarz (TODO)")
                state = NONE
        elif run.italic:
            if state == TAB and strip.startswith("("):
                state = KEY
                text = text[1:]
            elif state == KEY_CHANGE:
                state = COMFORT_KEY
            elif state != KEY:
                state = SILENT_CHORD
        elif run.font.subscript:
            if is_chord_state(state):
                chord_state = BASE
            else:
                print(
                    f"Niespodziewany stan dla run: {run.text}, par: {par.text}, song: {title}, subscript poza akordem")
        elif run.font.superscript:
            if is_chord_state(state):
                chord_state = ADDITIONAL
            else:
                print(f"Niespodziewany stan dla run: {run.text}, par: {par.text}, superscript poza akordem")
        elif len(strip) > 0:
            if (state == TAB or state == TEXT) and strip.startswith('|'):
                state = REPETITION
            elif text == '→':
                state = KEY_CHANGE
            else:
                state = CHORD
                chord_state = NONE
        elif state != TEXT or len(strip) > 0:
            state = NONE

        if state == ALTERNATIVE_KEY:
            print(f'{title}\t has alternative keys')

        if state == TEXT:
            if run.italic and not line.text[-1].italic:
                textRun = ITextRun(text)
                textRun.italic = True
                line.text.append(textRun)
            elif run.underline and not line.text[-1].underline:
                textRun = ITextRun(text)
                textRun.underline = True
                line.text.append(textRun)
            elif line.text[-1].italic or line.text[-1].underline:
                line.text.append(ITextRun(text))
            else:
                line.text[-1].text += run.text
        elif state == REPETITION:
            line.repetition = True
            if len(strip) > 1:
                if len(strip) > 2 and strip[1] == 'x':
                    if strip[2] == '8':
                        line.repetitionEnd = -1
                    elif strip[2].isnumeric():
                        line.repetitionEnd = int(strip[2])
                    else:
                        print(f"Nieprawidłowa wartość powtórzenia dla run: {run.text}, par: {par.text}, song: {title}")
                else:
                    print(f"Nieprawidłowa wartość powtórzenia dla run: {run.text}, par: {par.text}, song: {title}")
        elif state == KEY:
            if original_key is not None:
                print(f"Zduplikowana sygnatura tonacji dla run: {run.text}, par: {par.text}, song: {title}")
            elif len(text) > 0:
                keys = text.split("-")
                if len(keys) > 1:
                    comfort_key = parse_key(keys[0], run, par, title)
                    max_comfort_key = parse_key(keys[1], run, par, title)
                else:
                    original_key = parse_key(keys[0], run, par, title)
        elif state == COMFORT_KEY:
            if original_key is None or comfort_key is not None:
                print(f"Zduplikowana sygnatura tonacji dla run: {run.text}, par: {par.text}, song: {title}")
            else:
                comfort_key = parse_key(text, run, par, title)
        elif state == CHORD or state == SILENT_CHORD:
            if chord_state == BASE or chord_state == ADDITIONAL:
                chord: Optional[IChord] = None
                try:
                    if state == CHORD or state == SILENT_CHORD:
                        chord = line.chords.chords[-1].chords[-1].chord
                    elif state == ALTERNATIVE:
                        chord = line.chords.chords[-1].chords[-1].alternative
                    else:
                        print(f'Nieprawidłowy stan akordu: run: {text}, par: {par.text}, song: {title}')
                        raise Exception()
                except Exception:
                    print(
                        f'Nieprawidłowe miejsce wystąpienia składnika (nie ma ostatniego akordu): run: {text}, par: {par.text}, song: {title}')
                if chord_state == BASE:
                    if run.font.strike:
                        if text == '1':
                            chord.noPrime = True
                        else:
                            print(
                                f'Przekreślenie nuty w basie innej niż pryma: run: {text}, par: {par.text}, song: {title}')
                    else:
                        chord.base = IAdditionalSeries([])
                        if text.startswith("(") and text.endswith(")"):
                            chord.base.optional = True
                            text = text[1:-1]
                        bases = text.split("-")
                        for base in bases:
                            if not base[0].isnumeric():
                                print(
                                    f'Składnik w basie nie zaczyna się od numeru: run: {text}, par: {par.text}, song: {title}')
                            el = IElement(int(base[0]))
                            chord.base.elements.append(el)
                            if len(base) == 2:
                                if text[1] == "<":
                                    el.modification = "AUG"
                                elif text[1] == ">":
                                    el.modification = "DIM"
                                else:
                                    print(
                                        f'Nieprawidlowy modyfikator skladnika w basie: run: {text}, par: {par.text}, song: {title}')
                            elif len(base) > 2:
                                print(
                                    f'Nieprawidlowa dlugosc skladnika w basie: run: {text}, par: {par.text}, song: {title}')
                elif chord_state == ADDITIONAL:
                    chord.additionals = []
                    while True:
                        additional = IAdditionalSeries([])
                        chord.additionals.append(additional)
                        if text.startswith("(") and text.endswith(")"):
                            additional.optional = True
                            text = text[1:-1]
                        if text.startswith(' ') and len(text) > 1 and text[1].isnumeric():
                            text = text[1:]
                        elif not text[0].isnumeric():
                            print(
                                f'Składnik dodatkowy nie zaczyna się od numeru: run: {text}, par: {par.text}, song: {title}')
                        while True:
                            if text[0] == ' ':
                                text = text[1:]
                                if len(text) == 0 or text[0] != '-':
                                    break
                            el = IElement(int(text[0]))
                            additional.elements.append(el)
                            text = text[1:]
                            if len(text) > 0:
                                if text[0] == "<":
                                    el.modification = "AUG"
                                    text = text[1:]
                                elif text[0] == ">":
                                    el.modification = "DIM"
                                    text = text[1:]
                            if len(text) == 0 or text[0] != "-":
                                break
                            else:
                                text = text[1:]  # dodajemy kolejne opóźnienia
                        if len(text) == 0:
                            break  # jeśli nie to dodajemy kolejne składniki
            else:  # Normalny akord
                while len(text) > 0:
                    if text.startswith("("):
                        if not line.chords:
                            line.chords = IChords([])
                        line.chords.chords.append(IChordSeries([], optional=True))
                        if state == SILENT_CHORD:
                            line.chords.chords[-1].silent = True
                        text = text[1:]
                    elif text.startswith(")"):
                        if len(text) > 1:
                            if not line.chords:
                                line.chords = IChords([])
                            line.chords.chords.append(IChordSeries([]))
                            if state == SILENT_CHORD:
                                line.chords.chords[-1].silent = True
                        text = text[1:]
                    elif text.startswith("/"):
                        state = ALTERNATIVE
                        line.chords.chords[-1].chords[-1].alternative = IChord(INote("X"))
                        text = text[1:]
                    elif text.startswith("…"):
                        line.chords.chords[-1].repeat = True
                        text = text[1:]
                    elif text.startswith(" ") or text.startswith('\t'):
                        text = text[1:]
                    if len(text) == 0:
                        break
                    if text[0].lower() in "cdefgabh":
                        if not line.chords:
                            line.chords = IChords([IChordSeries([])])
                            if state == SILENT_CHORD:
                                line.chords.chords[-1].silent = True
                        if not state == ALTERNATIVE:
                            line.chords.chords[-1].chords.append(IComplexChord(IChord(INote("X"))))
                        chord = line.chords.chords[-1].chords[-1].chord if state != ALTERNATIVE else \
                            line.chords.chords[-1].chords[-1].alternative
                        chord.note.base = text[0].upper()
                        if chord.note.base == 'B':
                            chord.note.base = 'H'
                            chord.note.accidental = 'FLAT'
                        if text[0].islower():
                            chord.minor = True
                        text = text[1:]
                    if text.startswith("is"):
                        chord = line.chords.chords[-1].chords[-1].chord if state != ALTERNATIVE else \
                            line.chords.chords[-1].chords[-1].alternative
                        chord.note.accidental = 'SHARP'
                        text = text[2:]
                    elif text.startswith("s"):
                        chord = line.chords.chords[-1].chords[-1].chord if state != ALTERNATIVE else \
                            line.chords.chords[-1].chords[-1].alternative
                        chord.note.accidental = 'FLAT'
                        text = text[1:]
                    elif text.startswith("es"):
                        chord = line.chords.chords[-1].chords[-1].chord if state != ALTERNATIVE else \
                            line.chords.chords[-1].chords[-1].alternative
                        chord.note.accidental = 'FLAT'
                        text = text[2:]
                    if text.startswith("<"):
                        chord = line.chords.chords[-1].chords[-1].chord if state != ALTERNATIVE else \
                            line.chords.chords[-1].chords[-1].alternative
                        chord.modification = 'AUG'
                        text = text[1:]
                    elif text.startswith(">"):
                        chord = line.chords.chords[-1].chords[-1].chord if state != ALTERNATIVE else \
                            line.chords.chords[-1].chords[-1].alternative
                        chord.modification = 'DIM'
                        text = text[1:]
                    elif text.startswith("*"):
                        chord = line.chords.chords[-1].chords[-1].chord if state != ALTERNATIVE else \
                            line.chords.chords[-1].chords[-1].alternative
                        chord.modification = 'CLUSTER'
                        text = text[1:]

    lines.append(line)

    if indent is not None:
        indents = int((indent / 265430.0) + 0.9)
        for line in lines:
            if len(line.text[0].text) > 0:
                line.text[0].text = "\t" * indents + line.text[0].text

    return lines, (original_key, comfort_key, max_comfort_key)


def parse_key(text: str, run: Run, par: Paragraph, title: str) -> Optional[IKey]:
    if len(text) > 0 and text[0].lower() in 'cdefgabh':
        key = IKey(INote(text[0].upper()))
        if key.note.base == 'B':
            key.note.base = 'H'
            key.note.accidental = 'FLAT'
        if text[0].islower():
            key.minor = True
        text = text[1:]
        if text.startswith("is"):
            key.note.accidental = 'SHARP'
        elif text.startswith("s") or text.startswith("es"):
            key.note.accidental = 'FLAT'
        return key
    else:
        print(f"Nieprawidłowa sygnatura tonacji dla: {run.text}, par: {par.text}, song: {title}")
        return None


def verse_starts_with_short_line(verse: IVerse, short_line: ILine) -> bool:
    line = verse.lines[0]
    if not line.text:
        return False
    line_text = "".join(r.text for r in line.text)
    short_line_text = "".join(r.text for r in short_line.text)[:-1]
    return line_text.startswith(short_line_text)