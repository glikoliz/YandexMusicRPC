from pypresence import Presence
import time
from yandex_music import Client
from datetime import datetime
import re
import requests
import configparser
import os
import contextlib
import threading
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
        buttons=[{"label": "Кнопка", "url": f"https://music.yandex.ru/album/{track['albums'][0]['id']}/track/{track['id']}/"}],
        start=dstart,
        end=dsend,
    )
    if(get_log):
        print(
            f"Новый трек: {track.artists_name()[0]} - {track['title']} // {str(datetime.now()).split('.')[0]}"
        )


def GET_TOKEN_DISCORD():
    if len(config.get("TOKENS", "DSToken")) <= 5:
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
            print("ДС токен успешно получен")
            config.set("TOKENS", "DSToken", dst)
            with open("conf.ini", "w") as configfile:
                config.write(configfile)


def GET_TOKEN_MUSIC():
    if len(config.get("TOKENS", "MusicClient")) <= 5:
        print("Ключа нема")
        try:
            config.set("TOKENS", "MusicClient", token_ym.get_token())
            with open("conf.ini", "w") as configfile:
                config.write(configfile)
        except:
            print("Не получилось вытащить токен")


def init():  # читает все токены
    global headers, client, RPC, config
    config = configparser.ConfigParser()
    config.read("conf.ini")
    settings(config)
    if len(config.get("TOKENS", "MusicClient")) <= 5:
        print("[Яндекс Музыка] Установка необходимых пакетов.")
        os.system("pip install yandex-music --upgrade")
        os.system("pip install selenium")
        os.system("pip install pypresence")
        os.system("pip install yandex_music")
        os.system("pip install webdriver_manager")
    GET_TOKEN_MUSIC()
    if change_status:
        GET_TOKEN_DISCORD()
        headers = {
            "Authorization": config.get("TOKENS", "DSToken"),
        }
    RPC = Presence(config.get("TOKENS", "DSPresence"))
    RPC.connect()
    with contextlib.redirect_stdout(None):
        client = Client(config.get("TOKENS", "MusicClient")).init()


def update_status(text):
    if(change_status):
        requests.patch(
            "https://discord.com/api/v9/users/@me/settings",
            headers=headers,
            json={"custom_status": {"text": text}},
        )



def print_err(error):
    print(f"Ошибка: {str(error)} // {str(datetime.now()).split('.')[0]}")

def get_status():
    if(change_status):
        def_status = requests.get(
            "https://discord.com/api/v9/users/@me/settings", headers=headers
        )
        if def_status.status_code == 200:
            status_data = def_status.json()
            custom_status = status_data["custom_status"]
            if custom_status:
                status_text = custom_status["text"]
                # print(f"Текущий статус: {status_text}")
                return status_text
    else:
        print("Изменение статуса отключено")


def settings(config):
    global change_status, get_log
    try:
        change_status = config.getboolean("SETTINGS", "change_status")
        get_log=config.getboolean("SETTINGS", "get_log")
        print(f"Обновление статуса: {change_status}\nВедение лога: {get_log}")
    except:
        print("Не получилось получить значения из conf.ini")

init()
status_text = get_status()
# help('modules')
prev_track = None
i = 0
text = False
isError = False
while True:
    # try:
        last_track = (
            client.queue(client.queues_list()[0].id).get_current_track().fetch_track()
        )  # получает текущий трек
        cover = last_track.get_cover_url()  # ссылка на обложку текущего трека
        # при смене трека
        if prev_track != last_track:
            start = time.time()
            # threading.Thread(target=update_presence(last_track)).start()
            update_presence(last_track)
            if(change_status):
                try:
                    start_time = time.time()
                    # threading.Thread(target=update_status("")).start()
                    update_status("")

                    lyrics = last_track.get_lyrics("LRC").fetch_lyrics().split("\n")
                    mil = time_to_milliseconds(lyrics[0])
                    text = True
                except:
                    text = False
                    if(get_log):
                        print("У данной песни отсутствует текст")
            prev_track = last_track
            i = 0
            end_time = time.time()
            execution_time = end_time - start
            print(f"Время выполнения: {execution_time} секунд")
        # выводит текст в описание
        if(change_status):
            if text:
                now = time.time()
                if (now - start + execution_time) * 1000 > mil:
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
    # except Exception as error:
    #     if isError == False:
    #         isError = True
    #         update_status(status_text)
    #         print_err(error)
        # time.sleep(5)
