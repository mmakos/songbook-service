import json

from django.db import migrations

from Songbook.models import Source, SourceType


src_types = {
    'movie': 1,
    'musical': 2,
    'soundtrack': 3,
    'play': 4,
    'game': 5,
}


def map_source(src: dict) -> Source:
    source: Source = Source()
    source.id = src["id"]
    source.slug = src["slug"]
    source.type_id = src_types[src["type"]]
    source.name = src["name"]
    source.year = src["year"]
    source.url = src.get("url")

    return source


def migrate_sources(a, b):
    with open('data/sources.json', encoding='utf-8') as file:
        sources = json.load(file)
    for source in sources:
        src = map_source(source)
        src.save()


def migrate_source_types(a, b):
    for src_type, type_id in src_types.items():
        t = SourceType()
        t.id = type_id
        t.slug = src_type
        t.save()


class Migration(migrations.Migration):
    dependencies = [
    ]

    operations = [
        migrations.RunPython(migrate_source_types),
        migrations.RunPython(migrate_sources)
    ]
