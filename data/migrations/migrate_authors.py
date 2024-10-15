import json

from django.db import migrations

from Songbook.models import Person


def map_author(author: dict) -> Person:
    person: Person = Person()
    person.id = author["id"]
    person.slug = author["slug"]
    person.name = author["name"]
    person.second_name = author.get("secondName")
    person.last_name = author["lastName"]
    person.nickname = author.get("nickname")
    person.url = author.get("url")
    person.force_second_name = author.get("forceSecondName", False)
    person.force_nickname = author.get("forceNickname", False)

    return person


def migrate_authors(a, b):
    with open('data/authors.json', encoding='utf-8') as file:
        authors = json.load(file)
    for author in authors:
        person = map_author(author)
        person.save()


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.RunPython(migrate_authors)
    ]
