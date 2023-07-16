from pypresence import Presence
import time
from yandex_music import Client
from datetime import datetime
import re
import requests
import configparser

def time_to_milliseconds(time_string):
    match = re.search(r'\[(\d{2}):(\d{2}).(\d{2})\]', time_string)
    if match:
        minutes, seconds, milliseconds = map(int, match.groups())
        total_milliseconds = (minutes * 60 + seconds) * 1000 + milliseconds
        return total_milliseconds
    return None


def update_presence(track):
    dstart = time.time()  # начало трека в мс
    dsend = track["duration_ms"] / 1000 + time.time()  # конец трека в мс
    RPC.update(
        large_image=track.get_cover_url(),
        large_text="Чё смотришь",
        small_image="ym",
        small_text="ЯнДеКс МуЗыКа",
        details=track.artists_name()[0],
        state=track["title"],
        buttons=[{"label": "Кнопка", "url": "https://s.anizam.ru/l/bIY"}],
        start=dstart,
        end=dsend,
    )
    print(
        f"Новый трек: {track.artists_name()[0]} - {track['title']} // {str(datetime.now()).split('.')[0]}"
    )

config = configparser.ConfigParser()
config.read('conf.ini')
RPC = Presence(config.get('DSPresence', 'key'))
RPC.connect()
client = Client(config.get('MusicClient', 'key')).init()
prev_track = None
headers = {
    'Authorization': config.get('DSToken', 'key'),
}
data = {
    'custom_status': {
        'text': "",
        'emoji_id': None,
        'emoji_name': None
    }
}
i = 0
text = False
start = time.time()
while True:
    try:
        last_track = client.queue(client.queues_list()[0].id).get_current_track().fetch_track()  # получает текущий трек
        cover = last_track.get_cover_url()  # ссылка на обложку текущего трека
        if prev_track != last_track:
            start = time.time()
            update_presence(last_track)
            try:
                data['custom_status']['text'] = ""
                requests.patch('https://discord.com/api/v9/users/@me/settings', headers=headers, json=data)
                lyrics = last_track.get_lyrics('LRC').fetch_lyrics().split('\n')
                mil = time_to_milliseconds(lyrics[0])
                text = True
            except:
                text = False
                print("У данной песни отсутствует текст")
            prev_track = last_track
            i = 0
        if text:
            now = time.time()
            if (now - start + 1) * 1000 > mil:
                try:
                    data['custom_status']['text'] = lyrics[i].split("]")[1].strip()
                    requests.patch('https://discord.com/api/v9/users/@me/settings', headers=headers, json=data)
                except Exception as error:
                    print(f"{str(error)} // {datetime.now()}")
                i += 1
                try:
                    mil = time_to_milliseconds(lyrics[i])
                except:
                    text = False
    except Exception as error:
        print(f"{str(error)} // {datetime.now()}")
        time.sleep(5)