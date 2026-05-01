import time
import math
import random

from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import dearpygui.dearpygui as dpg

import Libs.Networking
import Libs.General
import Vars.OSINT
from Libs.Networking import user_agents

from Libs.Wrappers import GitHub
from Libs import Networking

import themes

from Libs.ConfigManager import config
from Vars import Protections

from Vars.General import console, scrapper, Errors
from Vars.OSINT import Protections

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
        themes.set_colored_result(result_text, default_error_result_text, "Red")
        console.print(e, style="red")

search_list = []

def add_username_search_thing(name:str, url:str, user_format:str=None, not_found_text=["Not Found", "404 Not Found"], headers:dict={}, user_agent:str="", error_url:str="", protections:list=[], extra_info=None, special=None):
    if not user_format:
        user_format = url
    search_list.append({
        "name": name,
        "url": url,
        "not_found_text": not_found_text,
        "user_format": user_format,
        "headers": headers,
        "user_agent": user_agent,
        "error_url": error_url,
        "protections": protections,
        "extra_info": extra_info,
        "special": special
    })

bot_check_things = [
    '<base href="https://www.google.com/recaptcha/challengepage/">',
    '<title>Just a moment...</title>',
    'https://challenges.cloudflare.com;',
    "<title>Attention Required! | Cloudflare</title>",
    "Please stand by, while we are checking your browser",
    '<span data-translate="checking_browser">Checking your browser before accessing</span>',
    'This website is using a security service to protect itself from online attacks.',
    '<title>Доступ ограничен</title>',
    'Verifying your browser, please wait...<br>DDoS Protection by</font> Blazingfast.io',
    '404</h1><p class="error-card__description">Мы&nbsp;не&nbsp;нашли страницу',
    'Доступ к информационному ресурсу ограничен на основании Федерального закона',
    'Incapsula incident ID',
    '<title>Client Challenge</title>',
    '<title>DDoS-Guard</title>',
    'Сайт заблокирован хостинг-провайдером',
    'Generated by cloudfront (CloudFront)',
    '/cdn-cgi/challenge-platform/h/b/orchestrate/chl_page',
    'captcha-sec.php'
]

def check_account(username, search):
    try:
        account_placeholders = {
            "username": username,
            "timestamp": str(math.floor(time.time()))
        }

        url = Libs.General.replace_placeholders(search["url"], account_placeholders)
        headers = search["headers"].copy()
        if search["user_agent"] != "":
            user_agent = search["user_agent"]
        else:
            user_agent = Libs.Networking.get_user_agent()
        headers["User-Agent"] = user_agent

        protections = search.get("protections", [])

        if Protections.CLOUDFLARE in protections:
            res = scrapper.get(url, allow_redirects=True, headers=headers, proxies=Libs.Networking.get_proxies(), timeout=10)
        else:
            res = requests.get(url, allow_redirects=True, headers=headers, proxies=Libs.Networking.get_proxies(), timeout=10)

        check_response = {
            "name": search["name"],
            "url": Libs.General.replace_placeholders(search["user_format"], account_placeholders)
        }

        text = res.text.lower()
        for part in bot_check_things:
            if part.lower() in text:
                check_response["error"] = Errors.BOT_DETECTION

        if res.status_code == 429:
            check_response["error"] = Errors.RATE_LIMIT

        if res.status_code == 403:
            check_response["error"] = Errors.UNAUTHORIZED

        if check_response.get("error"):
            return check_response

        not_found_text_check = False

        if isinstance(search["not_found_text"], str):
            not_found_text_check = search["not_found_text"].lower() in text
        elif isinstance(search["not_found_text"], list):
            not_found_text_check = any(not_found_text.lower() in text for not_found_text in search["not_found_text"])

        not_found = False
        if res.status_code == 404:
            not_found = True

        if not_found_text_check:
            not_found = True

        if res.url == search["error_url"]:
            not_found = True

        #print(username)
        #print(search)
        #print(res.status_code)
        #print(res.text[::100])
        #print(res.request.headers)

        if not_found:
            return None

        res.raise_for_status()
        return check_response

    except requests.HTTPError as e:
        check_response["error"] = f"had an {e.response.status_code} http error on {search['name']} :("
        console.print(e, style="red")
        return check_response
    except requests.Timeout:
        check_response["error"] = Errors.TIMEOUT
        return check_response
    except Exception as e:
        console.print(e, style="red")
        check_response["error"] = Errors.GENERAL
        return check_response


def username_search():
    if not search_list:
        add_username_search_thing("GitHub", "https://api.github.com/users/[username]", "https://github.com/[username]")
        add_username_search_thing("Minecraft", "https://api.mojang.com/users/profiles/minecraft/[username]", "https://namemc.com/profile/[username]")
        add_username_search_thing("YouTube", "https://www.youtube.com/@[username]")
        add_username_search_thing("TikTok", "https://www.tiktok.com/@[username]", not_found_text="Couldn't find this account")
        add_username_search_thing("Telegram", "https://t.me/[username]", not_found_text="https://telegram.org/img/t_logo_2x.png")
        add_username_search_thing("Scratch", "https://scratch.mit.edu/users/[username]", not_found_text="Our server is Scratch'ing its head")
        add_username_search_thing("Twitch", "https://twitchtracker.com/[username]", "https://www.twitch.tv/[username]")
        add_username_search_thing("Picsart", "https://api.picsart.com/users/show/[username].json", "https://picsart.com/u/[username]", not_found_text="user_not_found")
        add_username_search_thing("Substack", "https://substack.com/api/v1/user/[username]/public_profile", "https://substack.com/@[username]", not_found_text='profile not found')
        add_username_search_thing("OpenSea", "https://opensea.io/accounts/[username]")
        add_username_search_thing("Kaggle", "https://www.kaggle.com/[username]", not_found_text="We can't find that page.")
        add_username_search_thing("Hashnode", "https://hashnode.com/[username]", "User not found")
        add_username_search_thing("Vero", "https://vero.co/[username]", "not-found-page-container")
        add_username_search_thing("Pastebin", "https://pastebin.com/u/[username]", not_found_text="Not Found (#404)")
        add_username_search_thing("Chess.com", "https://www.chess.com/member/[username]", not_found_text="404 Page not found")
        add_username_search_thing("Itch.io", "https://itch.io/profile/[username]", not_found_text="We couldn't find your page")
        add_username_search_thing("Roblox", "https://www.roblox.com/user.aspx?username=[username]", not_found_text="Page Not found")
        add_username_search_thing("Genius", "https://genius.com/[username]", not_found_text="Oops! Page not found")
        add_username_search_thing("Interpals", "https://www.interpals.net/[username]", not_found_text="User not found")
        add_username_search_thing("GOG", "https://www.gog.com/u/[username]", not_found_text="error404")
        add_username_search_thing("Pokemon Showdown", "https://pokemonshowdown.com/users/[username]", not_found_text="(Unregistered)")
        add_username_search_thing("Duolingo", "https://www.duolingo.com/2023-05-23/users?fields=users&username=[username]&_=[timestamp]", "https://www.duolingo.com/profile/[username]", not_found_text='"users":[]')
        add_username_search_thing("Speaker Deck", "https://speakerdeck.com/[username]", not_found_text="User Not Found")
        add_username_search_thing("Steam", "https://steamcommunity.com/id/[username]", not_found_text="The specified profile could not be found.")
        add_username_search_thing("ReactOS", "https://reactos.org/wiki/User:[username]", not_found_text="is not registered")
        add_username_search_thing("NeedRom", "https://www.needrom.com/author/[username]", not_found_text="error_page")
        add_username_search_thing("Buzznet", "https://www.buzznet.com/author/[username]", not_found_text="error404")
        add_username_search_thing("Arduino", "https://projecthub.arduino.cc/[username]", not_found_text="error_image-wrapper")
        add_username_search_thing("House-Mixes.com", "https://www.house-mixes.com/[username]", not_found_text="next-error")
        add_username_search_thing("Subeta", "https://subeta.net/users/[username]", error_url="https://subeta.net/index.php")
        add_username_search_thing("Giphy", "https://giphy.com/channel/[username]", not_found_text="Oops! There’s nothing here.")
        add_username_search_thing("Gravatar", "https://en.gravatar.com/[username].json", not_found_text="User not found")
        add_username_search_thing("Reddit", "https://api.reddit.com/user/[username]/about", not_found_text="Not Found")
        add_username_search_thing("GitLab", "https://gitlab.com/[username]", error_url="https://gitlab.com/users/sign_in", protections=[Protections.CLOUDFLARE]) # this is so stupid, but if it works it works.

    result_text = "osint.username_search_result_text"
    user = dpg.get_value("osint.username_search_username_input").strip()

    if not user:
        themes.set_colored_result(result_text, "you kinda forgot the username...", "Red")
        return

    found_accounts = []

    usernames = user.splitlines()

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = []

        for username in usernames:
            for search in search_list:
                futures.append(executor.submit(check_account, username, search))

        for future in as_completed(futures):
            result = future.result()

            if result:
                if result.get("error"):
                    if isinstance(result["error"], int):
                        if result["error"] == Errors.BOT_DETECTION:
                            err_msg = f"we got detected on {result['name']} :("
                        elif result["error"] == Errors.TIMEOUT:
                            err_msg = f"they no respond on {result['name']} :("
                        elif result["error"] == Errors.UNAUTHORIZED:
                            err_msg = f"we no allowed on {result['name']} :("
                        elif result["error"] == Errors.RATE_LIMIT:
                            err_msg = f"we too fast on {result['name']} :("
                        else:
                            err_msg = f"had an error on {result['name']} :("
                    else:
                        err_msg = result["error"]

                    themes.set_colored_result(
                        result_text,
                        err_msg,
                        "Red"
                    )
                else:
                    found_accounts.append(result)
                    themes.set_colored_result(
                        result_text,
                        f"found user on {result['name']} :3",
                        "Green"
                    )

    if found_accounts:
        info_text = f"found {len(found_accounts)} accounts :3\n\n"
        for account in found_accounts:
            info_text += f"{account['name']}: {account['url']}\n"

        themes.set_colored_result(result_text, info_text, "Mauve")
    else:
        themes.set_colored_result(result_text, "accounts no found :(", "Red")