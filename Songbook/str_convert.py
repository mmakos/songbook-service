replacements = {
    u'ę': 'e',
    u'ó': 'o',
    u'ą': 'a',
    u'ś': 's',
    u'ł': 'l',
    u'ż': 'z',
    u'ź': 'z',
    u'ć': 'c',
    u'ń': 'n',
    u'í': 'i',
    u'ä': 'a',
    u'ü': 'u',
    u'è': 'e',
    u'é': 'e',
    u'á': 'e',
    u'ö': 'o',
    u'ő': 'o',
    u'č': 'c',
    u'ű': 'u',
    u'æ': 'a',
    u'ø': 'o',
    u'š': 's',
    u'đ': 'd',
}

def title_to_unique_name(title: str) -> str:
    filename = replace(
        ''.join(x.lower() for x in "-".join(title.split(" ")) if x.isalpha() or x.isnumeric() or x == "-")).encode(
        "ascii", "ignore").decode()
    if filename.isnumeric():
        filename = "a" + filename
    return filename


def replace(string):
    return ''.join(replacements.get(c, c) for c in string)

