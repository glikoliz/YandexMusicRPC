import json
from time import sleep

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.remote.command import Command
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


def is_active(driver):
    try:
        driver.execute(Command.GET_ALL_COOKIES)
        return True
    except Exception:
        return False


def get_token():
    capabilities = DesiredCapabilities.CHROME
    capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}
    
    service = Service(executable_path=ChromeDriverManager(version="114.0.5735.90").install())
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(
        "https://oauth.yandex.ru/authorize?response_type=token&client_id=23cabbbdc6cd418abb4b39c32c41195d")
    token = None    
    while token == None and is_active(driver):
        sleep(1)
        try:
            logs_raw = driver.get_log("performance")
        except:
            pass

        for lr in logs_raw:
            log = json.loads(lr["message"])["message"]
            url_fragment = log.get('params', {}).get('frame', {}).get('urlFragment')

            if url_fragment:
                token = url_fragment.split('&')[0].split('=')[1]

    try:
        driver.close()
    except:
        pass

    return token