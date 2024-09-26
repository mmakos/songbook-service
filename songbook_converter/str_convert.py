replacements = {
    u'ę': 'e',
    u'ó': 'o',
    u'ą': 'a',
    u'ś': 's',
    u'ł': 'l',
    u'ż': 'z',
    u'ź': 'z',
    u'ć': 'c',
    u'ń': 'n'
}

date_replacements = (
    "stycznia", "lutego", "marca", "kwietnia", "maja", "czerwca", "lipca", "sierpnia", "września", "października", "listopada", "grudnia"
)


def title_to_unique_name(title: str) -> str:
    filename = replace(
        ''.join(x.lower() for x in "-".join(title.split(" ")) if x.isalpha() or x.isnumeric() or x == "-")).encode(
        "ascii", "ignore").decode()
    if filename.isnumeric():
        filename = "a" + filename
    return filename


def normalize_for_search(string: str) -> str:
    return replace(string.encode('ascii', 'ignore').decode())


def replace(string):
    return ''.join(replacements.get(c, c) for c in string)


def replace_date(month):
    return date_replacements[month - 1]
