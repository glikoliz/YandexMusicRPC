from pypresence import Presence
import time
from yandex_music import Client
from datetime import datetime
import re
import requests
import configparser
import contextlib
from threading import Thread
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
        buttons=[
            {
                "label": "Открыть трек",
                "url": f"https://music.yandex.ru/album/{track['albums'][0]['id']}/track/{track['id']}/",
            }
        ],
        start=dstart,
        end=dsend,
    )
    # if get_log:
    #     print(
    #         f"Новый трек: {track.artists_name()[0]} - {track['title']} // {str(datetime.now()).split('.')[0]}"
    #     )


def GET_TOKEN_DISCORD(): #получает дс токен и записывает в конфиг
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


def GET_TOKEN_MUSIC(): #получает токен ям и записывает в конфиг
    if len(config.get("TOKENS", "MusicClient")) <= 5:
        print("Ключа нема")
        try:
            config.set("TOKENS", "MusicClient", token_ym.get_token())
            with open("conf.ini", "w") as configfile:
                config.write(configfile)
        except:
            print("Не получилось вытащить токен")


def init():  # читает все токены
    global headers, client, RPC, config, status_text
    config = configparser.ConfigParser()
    config.read("conf.ini")

    settings() #читает настройки с конфига
    GET_TOKEN_MUSIC()
    if change_status:
        GET_TOKEN_DISCORD()
        headers = {
            "Authorization": config.get("TOKENS", "DSToken"),
        }
    else:
        headers=None
    RPC = Presence(config.get("TOKENS", "DSPresence"))
    RPC.connect()
    with contextlib.redirect_stdout(None):
        client = Client(config.get("TOKENS", "MusicClient")).init()
    status_text = get_status()


def update_status(text): #обновляет статус
    global headers
    try:
        if change_status and headers:
            requests.patch(
                "https://discord.com/api/v9/users/@me/settings",
                headers=headers,
                json={"custom_status": {"text": text}},
            )
            return True
    except:
        return False


def print_err(error):
    print(f"Ошибка: {str(error)} // {str(datetime.now()).split('.')[0]}")


def get_status(): #получает текущий статус(до изменений)
    if change_status:
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


def settings():
    global change_status, get_log, headers
    try:
        change_status = config.getboolean("SETTINGS", "change_status")
        get_log = config.getboolean("SETTINGS", "get_log")
        # print(headers=="{'Authorization': ''}")
        if(change_status and headers==None):
            GET_TOKEN_DISCORD()
            headers = {
                "Authorization": config.get("TOKENS", "DSToken"),
            }
        # print(f"Обновление статуса: {change_status}\nВедение лога: {get_log}")
    except:
        change_status=False
        get_log=False
        print("Не получилось получить значения из conf.ini")


def main():
    global isError, last_track, prev_track, lyrics, mil, text, start, execution_time, i
    try:
        last_track = (
            client.queue(client.queues_list()[0].id)
            .get_current_track()
            .fetch_track()
        )
        if prev_track != last_track: #если трек меняется
            # testing.MainWindow.setlabel('Hitler')
            # label1.config(text=f"Сейчас играет - {last_track.title}")
            start = time.time()
            Thread(target=update_presence, args=[last_track]).start()
            if change_status:
                try:
                    Thread(target=update_status, args=[""]).start()
                    lyrics = last_track.get_lyrics("LRC").fetch_lyrics().split("\n")
                    mil = time_to_milliseconds(lyrics[0])
                    text = True
                    # label2.config(text="")
                except:
                    text = False
                    # label2.config(text="У данной песни отсутствует текст")
                    if get_log:
                        print("У данной песни отсутствует текст")
            prev_track = last_track
            i = 0
            end_time = time.time()
            execution_time = end_time - start
            # label2.config(text=f"Время выполнения: {round(execution_time, 4)} секунд")
            print(f"Время выполнения: {round(execution_time, 4)} секунд")
        if change_status and text: #транслирует текст в статус
            now = time.time()
            if (now - start + execution_time + 0.5) * 1000 > mil:
                try:
                    Thread(
                        target=update_status,
                        args=[lyrics[i].split("]")[1].strip()],
                    ).start()
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
        time.sleep(5)

def play_now():
    global last_track
    return last_track.title
    print()

def get_running(): #нужен для остановки функции loop
    return running
def main_loop():
    global status_text
    while(True):
        main()
        if(get_running()==False):
            # print("STOP")
            # print(update_status(status_text))
            # print(status_text)
            RPC.clear()
            break
def stop_loop():
    global running
    running=False
    # label1.config(text="")
    # label2.config(text="")
    if(change_status):
        update_status(status_text)
    # root.destroy()


def start_everything():
    global running
    global prev_track
    # label1.config(text="Начинаем")
    if(not running):
        prev_track=None
        running=True
        Thread(target=main_loop).start()

def change_config_status():
    global config
    try:
        if(config.getboolean("SETTINGS", "change_status")==False):
            config.set("SETTINGS", "change_status", 'True')
        else:
            config.set("SETTINGS", "change_status", 'False')
        with open("conf.ini", "w") as configfile:
            config.write(configfile)
        settings()
    except Exception as error:
        print_err(error)
        # config.set("SETTINGS", "change_status", "false")
        # print("sadasdsda")

if("__name__"!="__main__"):
    headers=None
    prev_track = None
    i = 0
    text = False
    isError = False
    running=False
    init()
    status_text=get_status()
    try:
        import win32gui, win32con
        # the_program_to_hide = win32gui.GetForegroundWindow()
        # win32gui.ShowWindow(the_program_to_hide , win32con.SW_HIDE)
    except:
        print()