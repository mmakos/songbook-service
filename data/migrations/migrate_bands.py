import json

from django.db import migrations

from Songbook.models import Band


def map_band(band_in: dict) -> Band:
    band: Band = Band()
    band.id = band_in["id"]
    band.slug = band_in["slug"]
    band.name = band_in["name"]
    band.url = band_in.get("url")

    return band


def migrate_bands(a, b):
    with open('data/bands.json', encoding='utf-8') as file:
        bands = json.load(file)
    for band in bands:
        person = map_band(band)
        person.save()


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.RunPython(migrate_bands)
    ]
