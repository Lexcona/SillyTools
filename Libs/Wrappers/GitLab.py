import time

import requests

import Libs
from Libs.ConfigManager import config

from Vars.General import console

session = requests.Session()

BASE_URL = "https://gitlab.com/api/v4"

def do_get(path:str, params:dict={}):
    return session.get(BASE_URL+path, params=params)

api_key = config.read("api_keys/gitlab")
if api_key:
    session.headers.update({"PRIVATE-TOKEN": api_key})

def update_proxies():
    session.proxies = Libs.Networking.get_proxies()

def should_stop(status_code):
    stop_codes = (409, 404, 403, 401)
    if status_code in stop_codes:
        console.print(f"stopping: {status_code}", style="red")
        return True
    return False

def error_check(e:str):
    e = str(e).strip().lower()
    if "rate limit" in e:
        return "rate limit"
    return None

def is_gitlab_email(email:str):
    email = email.lower().strip()
    domains = [
        "@users.noreply.gitlab.com",
        "noreply@gitlab.com",
        "@noreply.gitlab.com"
    ]

    for domain in domains:
        if email.endswith(domain):
            return True
    return False

def get_user(username:str, email:bool=False):
    update_proxies()
    try:
        params = {
            "username": username
        }
        res = do_get(f"/users", params=params)
        res.raise_for_status()
        data = res.json()

        if not data or len(data) == 0:
            return False

        data = data[0]

        if email:
            return data.get("public_email")

        return data
    except requests.exceptions.HTTPError as e:
        console.print(e, style="red")
        if error_check(e) == "rate limit":
            return 429
        if res.status_code == 404:
            return False

def check_real_user(username):
    try:
        user = get_user(username)
        if not user:
            return False

        return True
    except requests.exceptions.HTTPError as e:
        console.print(e, style="red")

def get_repos(username:str, just_repos:bool=True, id_only:bool=False):
    user = get_user(username)

    if not user:
        return False

    user_id = user["id"]

    update_proxies()
    page = 1
    repos = []
    while True:
        try:
            params = {
                "per_page": 100,
                "page": page
            }

            res = do_get(f"/users/{user_id}/projects", params=params)

            if should_stop(res.status_code):
                break

            res.raise_for_status()

            data = res.json()
            if not data or len(data) == 0:
                break

            for repo in data:
                if just_repos == True:
                    if id_only == True:
                        repos.append(repo["id"])
                    else:
                        repos.append(f'{repo["path_with_namespace"]}^_^{repo["id"]}')
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
                "author_username": username,
                "per_page": 100,
                "page": page
            }

            res = do_get(f"/issues", params=params)

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
    if api_key == None:
        return []

    update_proxies()
    page = 1
    commits = []
    while True:
        try:
            params = {
                "author_username": username,
                "state": "merged",
                "per_page": 100,
                "page": page
            }

            res = do_get(f"/merge_requests", params=params)

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

def get_emails(repo_id:int, username:str=None):
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
            res = do_get(f"/projects/{repo_id}/repository/commits", params=params)

            if should_stop(res.status_code):
                break

            res.raise_for_status()
            data = res.json()
            #print(data)

            if not data or len(data) == 0:
                break

            for commit in data:
                committer_email = commit.get("committer_email")
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
        if is_gitlab_email(email):
            emails.remove(email)
    return list(set(emails))