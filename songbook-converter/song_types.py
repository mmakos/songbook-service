from dataclasses import dataclass
from typing import List, Optional


@dataclass
class IntervalModification:
    modification: Optional[str]  # AUG, DIM


@dataclass
class IElement:
    interval: int
    modification: Optional[IntervalModification]
    optional: Optional[bool] = None


@dataclass
class IAdditionalSeries:
    elements: List[IElement]


@dataclass
class ChordModification:
    modification: Optional[str]  # AUG, DIM, CLUSTER


@dataclass
class Accidental:
    accidental: Optional[str]  # FLAT, SHARP


@dataclass
class NoteBase:
    base: str  # C, D, E, F, G, A, H


@dataclass
class INote:
    base: NoteBase
    accidental: Optional[Accidental] = None


@dataclass
class IChord:
    note: INote
    minor: Optional[bool] = None
    modification: Optional[ChordModification] = None
    base: Optional[IAdditionalSeries] = None
    additionals: Optional[List[IAdditionalSeries]] = None
    noPrime: Optional[bool] = None


@dataclass
class IComplexChord:
    chord: IChord
    alternative: Optional[IChord] = None


@dataclass
class IChordSeries:
    chords: List[IComplexChord]
    optional: Optional[bool] = None
    silent: Optional[bool] = None
    repeat: Optional[bool] = None


@dataclass
class IChords:
    chords: List[IChordSeries]
    alternatives: Optional[List[IChordSeries]] = None


@dataclass
class ITextRun:
    text: str
    italic: Optional[bool] = None
    underline: Optional[bool] = None
    bold: Optional[bool] = None


@dataclass
class ILine:
    text: List[ITextRun]
    repetition: Optional[bool] = None
    repetitionEnd: Optional[int] = None
    chords: Optional[IChords] = None
    comment: Optional[str] = None
    transposition: Optional[IChord] = None


@dataclass
class IVerse:
    lines: List[ILine]
    indent: int
    verseRef: Optional[int] = None


@dataclass
class INote:
    base: str
    accidental: Optional[str] = None


@dataclass
class IKey:
    note: INote
    minor: Optional[bool] = None


@dataclass
class ISongKey:
    songbook: IKey
    original: Optional[IKey] = None
    comfort: Optional[List[IKey]] = None


@dataclass
class IPerformance:
    url: str


@dataclass
class ISongOverview:
    id: str
    title: str


@dataclass
class ICategory:
    id: str
    name: str


@dataclass
class IEditorInfo:
    name: str
    time: float
    userVerified: Optional[bool] = None
    verified: Optional[bool] = None


@dataclass
class IAuthor:
    name: str
    lastName: Optional[str] = None


@dataclass
class ISong:
    id: str
    title: str
    category: ICategory
    created: IEditorInfo
    key: ISongKey
    verses: List[IVerse]
    edited: Optional[IEditorInfo] = None
    lyrics: Optional[List[IAuthor]] = None
    composer: Optional[List[IAuthor]] = None
    translation: Optional[List[IAuthor]] = None
    performers: Optional[List[IAuthor]] = None
    performances: Optional[List[IPerformance]] = None
    language: Optional[str] = None
    next: Optional[ISongOverview] = None
    previous: Optional[ISongOverview] = None
