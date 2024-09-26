from dataclasses import dataclass
from typing import List, Optional


@dataclass
class IElement:
    interval: int
    modification: Optional[str] = None  # AUG, DIM


@dataclass
class IAdditionalSeries:
    elements: List[IElement]
    optional: Optional[bool] = None


@dataclass
class INote:
    base: str  # C, D, E, F, G, A, H
    accidental: Optional[str] = None  # FLAT, SHARP


@dataclass
class IChord:
    note: INote
    minor: Optional[bool] = None
    modification: Optional[str] = None  # AUG, DIM, CLUSTER
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
    text: Optional[List[ITextRun]] = None
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
    comfort: Optional[IKey] = None
    maxComfort: Optional[IKey] = None


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
    verses: List[IVerse]
    key: Optional[ISongKey] = None
    edited: Optional[IEditorInfo] = None
    lyrics: Optional[List[IAuthor]] = None
    composer: Optional[List[IAuthor]] = None
    translation: Optional[List[IAuthor]] = None
    performers: Optional[List[IAuthor]] = None
    performances: Optional[List[IPerformance]] = None
    language: Optional[str] = None
    next: Optional[ISongOverview] = None
    previous: Optional[ISongOverview] = None
