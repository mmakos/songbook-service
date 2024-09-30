import json
import os

bands = []

for filename in os.listdir('songs_manual'):
    if filename.endswith(".json"):
        f = os.path.join('songs_manual', filename)
        with open(f, 'r', encoding='utf-8') as file:
            song = json.load(file)
        band = song.get("band")
        if band is not None and band not in bands:
            bands.append(band)

bands = [{"name": band["name"], "id": i + 100} for i, band in enumerate(bands)]

with open('data/bands.json', 'w', encoding='utf-8') as file:
    file.write(json.dumps(bands, indent=2, ensure_ascii=False))

        # performers = song.get("performers")
        # if performers is None:
        #     continue

        # band = None
        # performers_out = []
        # for performer in performers:
        #     if band is not None:
        #         performers_out.append(performer)
        #         continue
        #     if performer.get("name").upper() == "T" and performer.get("lastName").upper() == "LOVE":
        #         band = {"name": "T.Love"}
        #     elif performer.get("name").lower() == "koniec" and performer.get("lastName").lower() == "świata":
        #         band = {"name": "Koniec Świata"}
        #     elif performer.get("name").lower() == "kult":
        #         band = {"name": "Kult"}
        #     elif performer.get("name").lower() == "the" and performer.get("lastName").lower() == "cranberries":
        #         band = {"name": "The Cranberries"}
        #     elif performer.get("name").lower() == "lady" and performer.get("lastName").lower() == "pank":
        #         band = {"name": "Lady Pank"}
        #     elif performer.get("name").lower() == "the" and performer.get("lastName").lower() == "beatles":
        #         band = {"name": "The Beatles"}
        #     elif performer.get("name").lower() == "wspólnota" and performer.get("lastName").lower() == "miłości ukrzyżowanej":
        #         band = {"name": "Wspólnota Miłości Ukrzyżowanej"}
        #     elif performer.get("name").lower() == "elektryczne" and performer.get("lastName").lower() == "gitary":
        #         band = {"name": "Elektryczne Gitary"}
        #     elif performer.get("name").lower() == "czerwone" and performer.get("lastName").lower() == "gitary":
        #         band = {"name": "Czerwone Gitary"}
        #     elif performer.get("name").lower() == "kwiat" and performer.get("lastName").lower() == "jabłoni":
        #         band = {"name": "Kwiat Jabłoni"}
        #     elif performer.get("name").lower() == "pink" and performer.get("lastName").lower() == "floyd":
        #         band = {"name": "Pink Floyd"}
        #     elif performer.get("name").lower() == "ryczące" and performer.get("lastName").lower() == "dwudziestki":
        #         band = {"name": "Ryczące Dwudziestki"}
        #     elif performer.get("name").lower() == "budka" and performer.get("lastName").lower() == "suflera":
        #         band = {"name": "Budka Suflera"}
        #     elif performer.get("name").lower() == "image" and performer.get("lastName").lower() == "dragons":
        #         band = {"name": "Image Dragons"}
        #     elif performer.get("name").lower() == "wyspy" and performer.get("lastName").lower() == "dobrej nadziei":
        #         band = {"name": "Wyspy Dobrej Nadziei"}
        #     elif performer.get("name").lower() == "wolna" and performer.get("lastName").lower() == "grupa bukowina":
        #         band = {"name": "Wolna Grupa Bukowina"}
        #     elif performer.get("name").lower() == "cisza" and performer.get("lastName").lower() == "jak ta":
        #         band = {"name": "Cisza jak ta"}
        #     elif performer.get("name").lower() == "wały" and performer.get("lastName").lower() == "jagiellońskie":
        #         band = {"name": "Wały Jagiellońskie"}
        #     elif performer.get("name").lower() == "strachy" and performer.get("lastName").lower() == "na lachy":
        #         band = {"name": "Strachy na Lachy"}
        #     elif performer.get("name").lower() == "golec" and performer.get("lastName").lower() == "uorkiestra":
        #         band = {"name": "Golec uOrkiestra"}
        #     elif performer.get("name").lower() == "arka" and performer.get("lastName").lower() == "noego":
        #         band = {"name": "Arka Noego"}
        #     elif performer.get("name").lower() == "ekt" and performer.get("lastName").lower() == "gdynia":
        #         band = {"name": "EKT Gdynia"}
        #     elif performer.get("name").lower() == "brathanki":
        #         band = {"name": "Brathanki"}
        #     elif performer.get("name").lower() == "accantus":
        #         band = {"name": "Accantus"}
        #     elif performer.get("name").lower() == "hey":
        #         band = {"name": "HEY"}
        #     elif performer.get("name").lower() == "perfect":
        #         band = {"name": "Perfect"}
        #     elif performer.get("name").lower() == "sdm":
        #         band = {"name": "SDM"}
        #     elif performer.get("name").lower() == "myslovitz":
        #         band = {"name": "Myslovitz"}
        #     elif performer.get("name").lower() == "enej":
        #         band = {"name": "Enej"}
        #     elif performer.get("name").lower() == "ot.to":
        #         band = {"name": "OT.TO"}
        #     elif performer.get("name").lower() == "dżem":
        #         band = {"name": "Dżem"}
        #     elif performer.get("name").lower() == "neokatechumenat":
        #         band = {"name": "Neokatechumenat"}
        #     elif performer.get("name").lower() == "taizé":
        #         band = {"name": "Taizé"}
        #     else:
        #         performers_out.append(performer)
        #
        # if len(performers) > 0:
        #     song["performers"] = performers_out
        # else:
        #     del song["performers"]
        #
        # if band is not None:
        #     song["band"] = band
        #
        # with open(f, 'w', encoding='utf-8') as file:
        #     file.write(json.dumps(song, ensure_ascii=False, indent=2))
