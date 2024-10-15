import json

from django.db import migrations

from Songbook.models import Category


def map_category(cat: dict) -> Category:
    category: Category = Category()
    category.id = cat["id"]
    category.slug = cat["slug"]

    return category


def migrate_categories(a, b):
    with open('data/sources.json', encoding='utf-8') as file:
        cats = json.load(file)
    for cat in cats:
        category = map_category(cat)
        category.save()


class Migration(migrations.Migration):
    dependencies = [
    ]

    operations = [
        migrations.RunPython(migrate_categories)
    ]
