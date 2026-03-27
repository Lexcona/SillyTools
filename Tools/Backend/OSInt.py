import time
import random

import requests
import dearpygui.dearpygui as dpg

from rich.console import Console

import Libs.Networking
import Libs.General

from Libs.Wrappers import GitHub
from Libs import Networking

from Libs.ConfigManager import config

import themes

console = Console()

def search_emails_callback(sender, app_data, user_data):
    result_text = "osint.github_email_search_input_result_text"

    username = dpg.get_value("osint.github_email_search_input").strip()

    if not username:
        themes.set_colored_result(result_text, "you kinda forgot the username...", "Red")
        return

    all_emails = []

    if "github.com" in username:
        username_split = username.split("/")
        while True:
            if username_split[-1].replace(" ", "") == "":
                username_split.pop(-1)
            else:
                break
        username = username_split[-1]

    themes.set_colored_result(result_text, f"checking if real user...", "Mauve")

    if not GitHub.check_real_user(username):
        themes.set_colored_result(result_text, "user no real :(", "Red")
        return

    themes.set_colored_result(result_text, "scanning profile", "Mauve")

    repos = GitHub.get_repos(username)
    if repos == 429:
        themes.set_colored_result(result_text, "we got rate limited :(", "Red")
        return

    themes.set_colored_result(result_text, f"found {len(repos)} repos :3", "Green")

    commits = GitHub.get_commits(username)
    if commits == 429:
        themes.set_colored_result(result_text, "we got rate limited :(", "Red")
        return

    themes.set_colored_result(result_text, f"found {len(commits)} commits :3", "Green")

    all_repos = list(set(repos + commits))

    if not all_repos:
        themes.set_colored_result(result_text, f"found no repos :(", "Yellow")
    else:
        last_scan = 0
        for repo in all_repos:
            themes.set_colored_result(result_text, f"scanning {repo}'s commits...", "Mauve")
            emails = GitHub.get_emails(repo, username)
            if emails == 429:
                themes.set_colored_result(result_text, "we got rate limited :(", "Red")
                return

            for email in emails:
                all_emails.append(email)

            if last_scan >= 20:
                delay = random.randint(30, 120)
                for i in range(delay):
                    themes.set_colored_result(result_text, f"waiting {delay-i} more seconds till scanning again...", "Mauve")
                    time.sleep(1)
                last_scan = 0
            last_scan += 1

    public_email = GitHub.get_user_profile(username)
    if public_email == 429:
        themes.set_colored_result(result_text, "we got rate limited :(", "Red")
        return

    if public_email:
        themes.set_colored_result(result_text, "found public email :3", "Green")
        all_emails.append(public_email)
    else:
        themes.set_colored_result(result_text, "no public email :(", "Yellow")

    event_emails = GitHub.get_event_emails(username)
    if event_emails == 429:
        themes.set_colored_result(result_text, "we got rate limited :(", "Red")
        return

    if event_emails:
        themes.set_colored_result(result_text, "found event emails :3", "Green")
        for email in event_emails:
            all_emails.append(email)
    else:
        themes.set_colored_result(result_text, "no event emails :(", "Yellow")

    all_emails = list(set(all_emails))

    if not all_emails:
        themes.set_colored_result(result_text, "no emails found :(", "Red")
    else:
        themes.set_colored_result(result_text, f"found {len(all_emails)} emails :3\n{'\n'.join(all_emails)}", "Mauve")

def ip_lookup(sender, app_data, user_data):
    result_text = "osint.ip_lookup_result_text"

    ip_addr = dpg.get_value("osint.ip_lookup_ip_input").strip()

    if not ip_addr:
        themes.set_colored_result(result_text, "you kinda forgot the ip address...", "Red")
        return

    themes.set_colored_result(result_text, f"looking up {ip_addr}...", "Mauve")

    try:
        params = {}
        api_key = config.read("api_keys/ipinfo")
        if api_key:
            params["token"] = api_key

        ip_results = Networking.get_ipinfo(ip_addr, api_key, True)
        if ip_results:
            ip_text = "found the ip info :3\n"
            ip_text += f"\n{ip_results}"

            themes.set_colored_result(result_text, ip_text, "Mauve")
        else:
            themes.set_colored_result(result_text, "ip no real :(", "Red")

    except Exception as e:
        themes.set_colored_result(result_text, "thing went boom :(", "Red")
        console.print(e, style="red")

search_list = [
    {
        "name": "GitHub",
        "url": "https://api.github.com/users/[username]",
        "not_found_text": "Not Found",
        "user_format": "https://github.com/[username]",
        "extra_info": None,
        "special": None
    },
    {
        "name": "Minecraft",
        "url": "https://api.mojang.com/users/profiles/minecraft/[username]",
        "not_found_text": "Not Found",
        "user_format": "[username]",
        "extra_info": None,
        "special": None
    },
]

def username_search():
    result_text = "osint.username_search_result_text"

    user = dpg.get_value("osint.username_search_username_input").strip()

    if not user:
        themes.set_colored_result(result_text, "you kinda forgot the username...", "Red")
        return

    try:
        found_accounts = []
        for username in user.splitlines():
            for search in search_list:
                themes.set_colored_result(result_text, f"checking {search['name']}", "Mauve")
                res = requests.get(Libs.General.replace_placeholders(search["url"], {"username": username}), allow_redirects=True, headers={"User-Agent": Libs.Networking.get_user_agent()}, proxies=Libs.Networking.get_proxies())
                if res.status_code == 404 or search["not_found_text"] in res.text:
                    themes.set_colored_result(result_text, f"user no found on {search['name']}", "Red")
                else:
                    themes.set_colored_result(result_text, f"found user on {search['name']}", "Green")
                    found_accounts.append({"name": search["name"], "url": Libs.General.replace_placeholders(search["user_format"], {"username": username})})

        if found_accounts:
            info_text = f"found {len(found_accounts)} accounts :3\n\n"
            for account in found_accounts:
                info_text += f"{account['name']}: {account['url']}\n"
            themes.set_colored_result(result_text, info_text, "Mauve")
        else:
            themes.set_colored_result(result_text, "accounts no found :(", "Red")
    except Exception as e:
        themes.set_colored_result(result_text, "thing went boom :(", "Red")
        console.print(e, style="red")