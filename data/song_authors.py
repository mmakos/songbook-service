import json
import os

for i, filename in enumerate(os.listdir('songs_manual')):
    if filename.endswith(".json"):
        f = os.path.join('songs_manual', filename)
        with open(f, encoding='utf-8') as file:
            song: dict = json.load(file)
            performer = song.get('performer')
            if performer and len(performer) == 1 and performer[0] == 100 \
                    and 'composer' not in song and 'lyrics' not in song:
                song['composer'] = performer
                song['lyrics'] = performer
                with open(f, 'w', encoding='utf-8') as file:
                    json.dump(song, file, indent=2, ensure_ascii=False)
