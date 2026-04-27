import time

import requests

import Libs
from Libs.ConfigManager import config

from Vars.General import console

session = requests.Session()

api_key = config.read("api_keys/github")
if api_key:
    session.headers.update({"Authorization": f"token {api_key}"})

def update_proxies():
    session.proxies = Libs.Networking.get_proxies()

def should_stop(status_code):
    stop_codes = (409, 404, 403)
    if status_code in stop_codes:
        return True
    return False

def error_check(e:str):
    e = str(e).strip().lower()
    if "rate limit" in e:
        return "rate limit"
    return None


def is_github_email(email:str):
    email = email.lower().strip()
    domains = [
        "@users.noreply.github.com",
        "noreply@github.com",
        "@noreply.github.com",
        "@noreply.githubassets.com"
    ]

    for domain in domains:
        if email.endswith(domain):
            return True
    return False

def check_real_user(username:str):
    update_proxies()
    try:
        res = session.get(f"https://api.github.com/users/{username}")
        if res.status_code == 404:
            return False
        res.raise_for_status()
        return True
    except requests.exceptions.HTTPError as e:
        console.print(e, style="red")
        if error_check(e) == "rate limit":
            return 429
        

def get_repos(username:str, just_repos:bool=True):
    update_proxies()
    page = 1
    repos = []
    while True:
        try:
            params = {
                "per_page": 100,
                "page": page
            }

            res = session.get(f"https://api.github.com/users/{username}/repos", params=params)

            if should_stop(res.status_code):
                break

            res.raise_for_status()

            data = res.json()
            if not data or len(data) == 0:
                break

            for repo in data:
                if just_repos == True:
                    repos.append(repo["full_name"])
                else:
                    repos.append(repo)

            if len(data) < 100:
                break
            page += 1
            time.sleep(0.5)

        except requests.exceptions.HTTPError as e:
            console.print(e, style="red")
            if error_check(e) == "rate limit":
                return 429
            time.sleep(5)
            
    return repos

def get_issues(username:str):
    update_proxies()
    page = 1
    issues = []
    while True:
        try:
            params = {
                "q": f"author:{username}",
                "per_page": 100,
                "page": page
            }

            res = session.get(f"https://api.github.com/search/issues", params=params)

            if should_stop(res.status_code):
                break

            res.raise_for_status()

            data = res.json()
            if not data or len(data) == 0:
                break

            for issue in data:
                issues.append(issue)

            if len(data) < 100:
                break
            page += 1
            time.sleep(0.5)

        except requests.exceptions.HTTPError as e:
            console.print(e, style="red")
            if error_check(e) == "rate limit":
                return 429
            time.sleep(5)
            
    return issues

def get_commits(username:str, just_repos:bool=True):
    update_proxies()
    page = 1
    commits = []
    while True:
        try:
            params = {
                "q": f"author:{username} type:pr is:merged",
                "per_page": 100,
                "page": page
            }

            res = session.get(f"https://api.github.com/search/issues", params=params)

            if should_stop(res.status_code):
                break

            res.raise_for_status()

            data = res.json()
            if not data or len(data.get("items")) == 0:
                break

            for commit in data["items"]:
                #print(commit)
                if just_repos == True:
                    repo_url = commit.get("repository_url")
                    if repo_url:
                        commits.append("/".join(repo_url.split("/")[-2:]))
                else:
                    commits.append(commit)

            if len(data) < 100:
                break
            page += 1
            time.sleep(0.5)

        except requests.exceptions.HTTPError as e:
            console.print(e, style="red")
            if error_check(e) == "rate limit":
                return 429
            time.sleep(5)
            
    return list(set(commits))

def get_user_profile(username:str, email:bool=True):
    update_proxies()
    try:
        res = session.get(f"https://api.github.com/users/{username}")
        res.raise_for_status()
        data = res.json()

        if not data or len(data) == 0:
            return

        if email:
            return data.get("email")

        return data
    except requests.exceptions.HTTPError as e:
        console.print(e, style="red")
        if error_check(e) == "rate limit":
            return 429

def get_event_emails(username: str):
    update_proxies()
    page = 1
    emails = []

    while True:
        try:
            params = {
                "per_page": 100,
                "page": page
            }

            res = session.get(f"https://api.github.com/users/{username}/events", params=params)

            if should_stop(res.status_code):
                break

            res.raise_for_status()

            data = res.json()
            if not data:
                break

            for event in data:
                if event.get("type") != "PushEvent":
                    continue

                for commit in event.get("payload", {}).get("commits", []):
                    email = commit.get("author", {}).get("email")
                    if email:
                        emails.append(email.lower().strip())

            if len(data) < 100:
                break

            page += 1
            time.sleep(0.5)

        except requests.exceptions.HTTPError as e:
            console.print(e, style="red")
            if error_check(e) == "rate limit":
                return 429
            time.sleep(5)
            
    for email in emails[::]:
        if is_github_email(email):
            emails.remove(email)
    return list(set(emails))

def get_emails(repo:str, username:str=None):
    update_proxies()
    emails = []
    page = 1

    while True:
        params = {
            "per_page": 100,
            "page": page
        }

        if username:
            params["author"] = username

        try:
            res = session.get(f"https://api.github.com/repos/{repo}/commits", params=params)

            if should_stop(res.status_code):
                break

            res.raise_for_status()
            data = res.json()
            #print(data)

            if not data or len(data) == 0:
                break

            for commit in data:
                commit = commit.get("commit")
                if commit:
                    author_email = commit.get("author", {}).get("email")
                    if author_email:
                        emails.append(author_email.lower().strip())

                    committer_email = commit.get("committer", {}).get("email")
                    if committer_email:
                        emails.append(committer_email.lower().strip())

            if len(data) < 100:
                break

            page += 1
            time.sleep(0.5)
        except requests.exceptions.HTTPError as e:
            console.print(e, style="red")
            if error_check(e) == "rate limit":
                return 429
            time.sleep(5)
    for email in emails[::]:
        if is_github_email(email):
            emails.remove(email)
    return list(set(emails))