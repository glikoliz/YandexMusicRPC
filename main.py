from pypresence import Presence
import time
from yandex_music import Client
from datetime import datetime
import re
import requests
import configparser
import os
#
import token_ym
import token_ds
#
def time_to_milliseconds(time_string):
    match = re.search(r"\[(\d{2}):(\d{2}).(\d{2})\]", time_string)
    if match:
        minutes, seconds, milliseconds = map(int, match.groups())
        total_milliseconds = (minutes * 60 + seconds) * 1000 + milliseconds
        return total_milliseconds
    return None


def update_presence(track):  # Обновляет статус активности
    dstart = time.time()  # начало трека в мс
    dsend = track["duration_ms"] / 1000 + time.time()  # конец трека в мс

    RPC.update(
        large_image=track.get_cover_url(),
        large_text="Чё смотришь",
        small_image="ym",
        small_text="ЯнДеКс МуЗыКа",
        details=track.artists_name()[0],
        state=track.title,
        buttons=[{"label": "Кнопка", "url": "https://s.anizam.ru/l/bIY"}],
        start=dstart,
        end=dsend,
    )
    print(
        f"Новый трек: {track.artists_name()[0]} - {track['title']} // {str(datetime.now()).split('.')[0]}"
    )


def GET_TOKEN_DISCORD():
    if len(config.get("DSToken", "key")) <= 5:
        print("ДС токен не обнаружен")
        dst = ""
        try:
            dst = token_ds.get_token()
        except:
            print("Не удалось подцепить токен")
        # print(requests.get('https://discord.com/api/v9/users/@me', headers={"Authorization": dst,}))
        if (
            requests.get(
                "https://discord.com/api/v9/users/@me",
                headers={
                    "Authorization": dst,
                },
            ).status_code
        ) == 200:
            print("ДС ТОКЕН УСПЕШНО СПИЗЖЕН")
            config.set("DSToken", "key", dst)
            with open("conf.ini", "w") as configfile:
                config.write(configfile)


def GET_TOKEN_MUSIC():
    if len(config.get("MusicClient", "key")) <= 5:
        print("Ключа нема")
        try:
            config.set("MusicClient", "key", token_ym.get_token())
            with open("conf.ini", "w") as configfile:
                config.write(configfile)
        except:
            print("Не получилось вытащить токен")


def init():  # читает все токены

    global headers, client, RPC, config
    config = configparser.ConfigParser()
    config.read("conf.ini")
    if len(config.get("MusicClient","key")) <= 5:
        print("[Яндекс Музыка] Установка необходимых пакетов.")
        os.system('pip install yandex-music --upgrade')
        os.system('pip install selenium')
        os.system('pip install pypresence')
        os.system('pip install yandex_music')
        os.system('pip install webdriver_manager')
    GET_TOKEN_MUSIC()
    GET_TOKEN_DISCORD()
    RPC = Presence(config.get("DSPresence", "key"))
    RPC.connect()
    client = Client(config.get("MusicClient", "key")).init()
    # clear = lambda: os.system('cls')
    # clear()
    headers = {
        "Authorization": config.get("DSToken", "key"),
    }


def update_status(text):
    requests.patch(
        "https://discord.com/api/v9/users/@me/settings",
        headers=headers,
        json={"custom_status": {"text": text}},
    )

def print_err(error):
    print(f"Ошибка: {str(error)} // {str(datetime.now()).split('.')[0]}")

init()
status_text=""
def_status=requests.get("https://discord.com/api/v9/users/@me/settings",headers=headers)
if def_status.status_code == 200:
    status_data = def_status.json()
    custom_status = status_data['custom_status']
    if custom_status:
        status_text = custom_status['text']
        print(f'Текущий статус: {status_text}')
prev_track = None
i = 0
text = False
isError = False
while True:
    try:
        last_track = (
            client.queue(client.queues_list()[0].id).get_current_track().fetch_track()
        )  # получает текущий трек
        cover = last_track.get_cover_url()  # ссылка на обложку текущего трека
        # при смене трека
        if prev_track != last_track:
            start = time.time()
            update_presence(last_track)
            try:
                update_status("")
                lyrics = last_track.get_lyrics("LRC").fetch_lyrics().split("\n")
                mil = time_to_milliseconds(lyrics[0])
                text = True
            except:
                text = False
                print("У данной песни отсутствует текст")
            prev_track = last_track
            i = 0
        # выводит текст в описание
        if text:
            now = time.time()
            if (now - start + 1) * 1000 > mil:
                try:
                    update_status(lyrics[i].split("]")[1].strip())
                except Exception as error:
                    print_err(error)
                i += 1
                try:
                    mil = time_to_milliseconds(lyrics[i])
                except:
                    text = False
        isError = False
    except Exception as error:
        if isError == False:
            isError = True
            update_status(status_text)
            print_err(error)
        # time.sleep(5)