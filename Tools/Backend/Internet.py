import re
import os
import ssl
import time
import whois
import socket
import random
import threading
import urllib.parse
import concurrent.futures

from collections import deque
from queue import Queue, Empty

import dearpygui.dearpygui as dpg
import dns.resolver
import requests
import bs4

from dns.exception import DNSException
from bs4 import BeautifulSoup
from requests.structures import CaseInsensitiveDict

import Libs.Networking

import themes

from cryptography import x509
from cryptography.x509.oid import NameOID, ExtensionOID

from Libs.ConfigManager import config

from Vars.General import console

def search_domain_nameservers(sender, app_data, user_data):
    result_text = "internet.find_name_servers_result_text"

    domain = dpg.get_value("internet.find_name_servers_domain_input").strip()

    if not domain:
        themes.set_colored_result(result_text, "you kinda forgot the domain...", "Red")
        return

    themes.set_colored_result(result_text, "finding nameservers...", "Mauve")
    try:
        with Libs.Networking.proxy_socket(Libs.Networking.get_proxies()):
            nameservers_text = ""
            for nameserver in dns.resolver.resolve(domain, 'NS'):
                nameservers_text += nameserver.to_text() + "\n"
        themes.set_colored_result(result_text, f"found {domain}'s nameservers :3\n{nameservers_text}", "Mauve")
    except Exception as e:
        if "does not exist" in str(e):
            themes.set_colored_result(result_text, f"{domain} no exist :(", "Red")
        else:
            console.print(e, style="red")
            themes.set_colored_result(result_text, "thing went boom :(", "Red")

def ip_cert_lookup(sender, app_data, user_data):
    result_text = "internet.find_cert_domains_result_text"
    ip_addr = dpg.get_value("internet.find_cert_domains_ip_address_input").strip()
    if not ip_addr:
        themes.set_colored_result(result_text, "you kinda forgot the ip address...", "Red")
        return

    if ":" in ip_addr:
        ip_addr_split = ip_addr.split(":")
        ip_addr = ip_addr_split[0]
        port = ip_addr_split[-1]
    else:
        port = 443

    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_OPTIONAL

    common_name = ""
    san_domains = []

    try:
        themes.set_colored_result(result_text,f"connecting to {ip_addr}:{port}...","Mauve")
        with Libs.Networking.proxy_socket(Libs.Networking.get_proxies()):
            with socket.create_connection((ip_addr, port), timeout=30) as sock:
                with context.wrap_socket(sock, server_hostname=ip_addr) as ssock:
                    themes.set_colored_result(result_text, f"connected at {ip_addr}:{port} :3", "Green")
                    der_cert = ssock.getpeercert(binary_form=True)
                    if not der_cert:
                        themes.set_colored_result(result_text, "got no cert :(", "Red")
                        return

                    themes.set_colored_result(result_text, f"loading cert...", "Mauve")
                    cert = x509.load_der_x509_certificate(der_cert)

                    try:
                        raw_common_name = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
                        if raw_common_name:
                            common_name = raw_common_name[0].value
                            themes.set_colored_result(result_text, f"found common name {common_name} :3", "Green")
                    except Exception:
                        themes.set_colored_result(result_text, f"common name no found :(", "Red")
                        pass

                    try:
                        san_ext = cert.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
                        for name in san_ext.value.get_values_for_type(x509.DNSName):
                            themes.set_colored_result(result_text, f"found domain {name} :3", "Green")
                            san_domains.append(name)
                        for name in san_ext.value.get_values_for_type(x509.IPAddress):
                            themes.set_colored_result(result_text, f"found domain {str(name)} :3", "Green")
                            san_domains.append(str(name))
                    except x509.ExtensionNotFound:
                        pass
    except ssl.SSLError as e:
        themes.set_colored_result(result_text, "ssl went boom :(", "Red")
        console.print(f"SSL error:\n{e}", style="red")
        return
    except socket.timeout:
        themes.set_colored_result(result_text, "connection went boom :(", "Red")
        return
    except ConnectionRefusedError:
        themes.set_colored_result(result_text, "thing went no connect :(", "Red")
        return
    except Exception as e:
        themes.set_colored_result(result_text, "thing went boom :(", "Red")
        console.print(e, style="red")
        return

    themes.set_colored_result(result_text, f"found {len(san_domains)} domains on {ip_addr}:{port} :3\n\ncommon: {common_name}\nothers:\n{'\n'.join(san_domains)}", "Mauve")

def dns_dump(sender, app_data, user_data):
    result_text = "internet.domain_to_ip_result_text"
    domain = dpg.get_value("internet.domain_to_ip_domain_input").strip()
    if not domain:
        themes.set_colored_result(result_text, "you kinda forgot the domain...", "Red")
        return

    domain = domain.split("://")[-1].split("/")[0]

    record_types = [
        'A', 'AAAA', 'CNAME', 'MX', 'NS', 'SOA', 'TXT', 'PTR', 'SRV', 'CAA', 'DNSKEY', 'DS', 'TLSA', 'OPENPGPKEY', 'SSHFP', 'RP', 'LOC', 'HINFO', 'NAPTR', 'CERT', 'SPF', 'DMARC', 'DKIM',
    ]

    themes.set_colored_result(result_text, "getting dns records...", "Mauve")
    with Libs.Networking.proxy_socket(Libs.Networking.get_proxies()):
        resolver = dns.resolver.Resolver()
        resolver.timeout = 5
        resolver.lifetime = 6

        found_any = False

        dns_text = "found dns records :3\n"

        for rtype in record_types:
            try:
                qname = domain
                if rtype == 'DMARC':
                    qname = f"_dmarc.{domain}"
                elif rtype == 'DKIM':
                    print("DKIM: needs selector (skipping generic query)")
                    continue

                themes.set_colored_result(result_text, f"resolving {rtype}...", "Mauve")
                answers = resolver.resolve(qname, rtype)

                found_any = True
                dns_text += f"\n{rtype} records:\n"
                for rdata in answers:
                    if rtype in ('A', 'AAAA'):
                        service_tag = Libs.Networking.service_tag(rdata.address)
                        dns_text += f"{rdata.address} {service_tag}\n"
                    elif rtype == 'MX':
                        dns_text += f"priority {rdata.preference} > {rdata.exchange}\n"
                    elif rtype == 'TXT':
                        dns_text += f"{rdata.to_text().strip('"')}\n"
                    elif rtype == 'SOA':
                        dns_text += f"primary nameserver: {rdata.mname}\n"
                        dns_text += f"admin: {rdata.rname}\n"
                        dns_text += f"serial: {rdata.serial}\n"
                    else:
                        dns_text += f"{rdata.to_text()}\n"

            except dns.resolver.NoAnswer:
                pass
            except dns.resolver.NXDOMAIN:
                themes.set_colored_result(result_text, "domain no exist :(", "Red")
                return
            except dns.resolver.Timeout:
                themes.set_colored_result(result_text, f"timed out on {rtype} :(", "Red")
            except DNSException as e:
                themes.set_colored_result(result_text, f"dns went boom :(", "Red")
                console.print(e)

    themes.set_colored_result(result_text, dns_text, "Mauve")

    if not found_any:
        themes.set_colored_result(result_text, "no find records :(", "Red")

def url_clean(base_url: str, link: str):
    if not link:
        return None

    if link.startswith(('#', 'data:', 'javascript:', 'mailto:', 'tel:')):
        return None

    try:
        url = urllib.parse.urljoin(base_url, link.strip())
        parsed = urllib.parse.urlparse(url)

        if parsed.scheme not in ('http', 'https'):
            return None

        clean_url = urllib.parse.urlunparse((
            parsed.scheme,
            parsed.netloc.lower(),
            parsed.path or '/',
            parsed.params,
            parsed.query,
            ''
        ))
        return clean_url
    except Exception as e:
        console.print(e, style="red")
        return None

def classify_tag(tag: bs4.Tag):
    kind = ""

    if tag.name == "a":
        url_part = tag.get("href")
        kind = "page"
    elif tag.name in ("img", "source"):
        url_part = tag.get("src") or tag.get("data-src") or tag.get("srcset")
        kind = "image"
    elif tag.name in ("video", "source", "track"):
        url_part = tag.get("src")
        kind = "video"
    elif tag.name == "audio":
        url_part = tag.get("src")
        kind = "audio"
    elif tag.name == "script" and tag.get("src"):
        url_part = tag.get("src")
        kind = "script"
    elif tag.name == "link" and "stylesheet" in (tag.get("rel") or []):
        url_part = tag.get("href")
        kind = "stylesheet"
    elif tag.name == "iframe":
        url_part = tag.get("src")
        kind = "iframe"
    else:
        url_part = tag.get("src") or tag.get("href") or tag.get("data-src")
        if url_part:
            kind = "other"

    if not url_part:
        return "", ""

    return url_part.strip(), kind


def site_mapper(sender, app_data, user_data):
    max_threads = 16
    timeout = 10
    result_widget = "internet.site_mapper_result_text"

    url = dpg.get_value("internet.site_mapper_domain_input").strip()
    if not url:
        themes.set_colored_result(result_widget, "you kinda forgot the url...", "Red")
        return

    start_url = Libs.Networking.fix_url(url)
    domain = urllib.parse.urlparse(start_url).netloc

    session = requests.Session()
    session.headers["User-Agent"] = Libs.Networking.get_user_agent()
    session.proxies = Libs.Networking.get_proxies()

    did_urls = set()
    queue = [start_url]
    found_urls = {start_url}

    all_cats = {
        "page": set(),
        "image": set(),
        "video": set(),
        "audio": set(),
        "script": set(),
        "stylesheet": set(),
        "iframe": set(),
        "other": set()
    }

    lock = threading.Lock()
    count_thing = 0

    themes.set_colored_result(result_widget, f"crawling from {start_url}...", "Mauve")

    def fetch_and_parse(url):
        try:
            res = session.get(url, timeout=timeout)
            res.raise_for_status()

            if "text/html" not in res.headers.get("content-type", "").lower():
                return url, set(), {}

            soup = BeautifulSoup(res.text, "html.parser")

            new_pages = set()
            cats = {}
            for cat in all_cats:
                cats[cat] = set()

            for tag in soup.find_all():
                link_text, kind = classify_tag(tag)
                if not link_text:
                    continue

                link = url_clean(url, link_text)
                if not link:
                    continue

                if kind in cats:
                    cats[kind].add(link)

                if kind == "page" and urllib.parse.urlparse(link).netloc == domain:
                    new_pages.add(link)

            return url, new_pages, cats

        except Exception as e:
            console.print(e, style="red")
            return url, set(), {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        while queue:
            futures = []

            for i in range(min(max_threads, len(queue))):
                if queue:
                    next_url = queue.pop(0)
                    if next_url not in did_urls:
                        futures.append(executor.submit(fetch_and_parse, next_url))

            if not futures:
                break

            for future in concurrent.futures.as_completed(futures):
                url_done, new_pages, res_dict = future.result()

                with lock:
                    if url_done in did_urls:
                        continue

                    did_urls.add(url_done)
                    count_thing += 1

                    for cat, links in res_dict.items():
                        all_cats[cat].update(links)

                    for page in new_pages:
                        if page not in found_urls:
                            found_urls.add(page)
                            queue.append(page)

                    themes.set_colored_result(result_widget, f"crawled: {count_thing}\nqueue: {len(queue)}\ntotal unique: {len(found_urls)}", "Mauve")

    info_lines = []
    info_lines.append(f"crawled {count_thing} pages")
    info_lines.append(f"found {len(found_urls)} unique urls\n")

    for cat, urls in sorted(all_cats.items(), key=lambda x: -len(x[1])):
        if urls:
            info_lines.append(f"{cat} ({len(urls)} found):")
            for ex in sorted(urls):
                info_lines.append(f"  {ex}")
            info_lines.append("")

    info_lines.append("crawled pages:")
    for u in sorted(did_urls):
        info_lines.append(f"  {u}")

    themes.set_colored_result(result_widget, "\n".join(info_lines).strip(), "Mauve")

def tag_dumper():
    result_text = "internet.tag_dumper_result_text"

    url = dpg.get_value("internet.tag_dumper_url_input").strip()
    if not url:
        themes.set_colored_result(result_text, "you kinda forgot the url...", "Red")
        return

    url = Libs.Networking.fix_url(url)
    if not url:
        themes.set_colored_result(result_text, "no real url :(", "Red")
        return

    output = dpg.get_value("internet.tag_dumper_output_input").strip()
    if not output:
        output = f"./export/tag_dumper/{url.split('://')[-1].replace('/', '_')}"

    os.makedirs(output, exist_ok=True)

    headers = {
        "User-Agent": Libs.Networking.get_user_agent()
    }

    tag_count = {

    }
    themes.set_colored_result(result_text, "getting tags...", "Mauve")

    try:
        res = requests.get(url, headers=headers, proxies=Libs.Networking.get_proxies())
        res.raise_for_status()

        soup = BeautifulSoup(res.content, "html.parser")
        tags = soup.find_all()
        for tag in tags:
            tag_count[tag.name] = 0

        for tag in tags:
            tag_count[tag.name] = tag_count[tag.name] + 1
            themes.set_colored_result(result_text, f"found {tag.name} :3", "Mauve")

            dirm = output + "/" + tag.name

            os.makedirs(dirm, exist_ok=True)

            with open(dirm + "/" + str(tag_count[tag.name]) + ".html", "w+") as f:
                f.write(str(tag))

        with open(f"{output}/page.html", "w+") as f:
            f.write(res.text)

        tag_text = f"dumped all tags :3\n"
        for key, value in tag_count.items():
            tag_text += f"{key}: {value}\n"
        themes.set_colored_result(result_text, tag_text, "Mauve")

    except Exception as e:
        themes.set_colored_result(result_text, f"thing went boom :(", "Red")
        console.print(e, style="red")

def method_scanner():
    result_text = "internet.method_scanner_result_text"

    url = dpg.get_value("internet.method_scanner_url_input").strip()
    if not url:
        themes.set_colored_result(result_text, "you kinda forgot the url...", "Red")
        return

    url = Libs.Networking.fix_url(url)
    if not url:
        themes.set_colored_result(result_text, "no real url :(", "Red")
        return

    headers = {
        "User-Agent": Libs.Networking.get_user_agent()
    }

    valid_methods = []

    methods = [
        "GET",
        "POST",
        "PATCH",
        "PUT",
        "DELETE",
        "HEAD",
        "CONNECT",
        "OPTIONS",
        "TRACE"
    ]

    for method in methods:
        themes.set_colored_result(result_text, f"checking {method}...", "Mauve")
        res = requests.request(method, url, allow_redirects=True, headers=headers, proxies=Libs.Networking.get_proxies())

        if not res.status_code in (404, 405, 501):
            themes.set_colored_result(result_text, f"{method} valid :3", "Mauve")
            valid_methods.append(method)

    if valid_methods:
        info_text = f"found valid methods for {url} :3\n{'\n'.join(valid_methods)}"
        themes.set_colored_result(result_text, info_text, "Mauve")
    else:
        themes.set_colored_result(result_text, "no methods found :(", "Mauve")

def url_checker():
    result_text = "internet.url_checker_result_text"

    urls = dpg.get_value("internet.url_checker_urls_input").strip()
    if not urls:
        themes.set_colored_result(result_text, "you kinda forgot the urls...", "Red")
        return

    urls = urls.splitlines()

    valid_urls = []
    invalid_urls = []
    timed_urls = []

    for url in urls:
        themes.set_colored_result(result_text, f"checking {url}...", "Mauve")
        url_check = Libs.Networking.check_url(url)
        if url_check:
            themes.set_colored_result(result_text, f"{url} valid :3", "Mauve")
            valid_urls.append(url)
        elif url_check == "Timed Out":
            themes.set_colored_result(result_text, f"{url} timed out :(", "Red")
            timed_urls.append(url)
        else:
            themes.set_colored_result(result_text, f"{url} invalid :(", "Red")
            invalid_urls.append(url)
        time.sleep(random.randint(2, 50)/10)
    if valid_urls:
        url_text = "found valid urls :3\n\nvalid urls:\n"
        for url in valid_urls:
            url_text += f"{url}\n"
        url_text += "\ninvalid urls:\n"
        for url in invalid_urls:
            url_text += f"{url}\n"
        url_text += "\ntimed out urls:\n"
        for url in timed_urls:
            url_text += f"{url}\n"
        themes.set_colored_result(result_text, url_text, "Mauve")
    else:
        themes.set_colored_result(result_text, "no valid urls :(", "Red")

# Had a use but decided to leave it useless just incase.
def clean_headers(headers:CaseInsensitiveDict[str]):
    better_headers = {}
    usual_headers = [

    ]

    # This finds all the keys in the headers dictionary to see if it's a usual header that shows for web requests.
    # Basically a useless header remover.
    for key, value in headers.items():
        if not key.lower() in usual_headers:
            better_headers[key] = value
    return better_headers

def web_info_text_thing(res:requests.Response):
    info_text = ""
    info_text += f"url: {res.url}\n"
    if res.raw._connection:
        ip_addr = res.raw._connection.sock.getpeername()[0]
        info_text += f"ip: {ip_addr} {Libs.Networking.service_tag(ip_addr)}\n"
    info_text += f"status code: {res.status_code}\n"
    info_text += f"server: {res.headers.get('server', 'unknown')}\n"
    info_text += f"\nheaders:\n"
    for key, value in clean_headers(res.headers).items():
        info_text += f"{key}: {value}\n"
    info_text += "=======================\n"
    return info_text

def website_info():
    result_text = "internet.website_info_result_text"

    url = dpg.get_value("internet.website_info_url_input").strip()
    if not url:
        themes.set_colored_result(result_text, "you kinda forgot the url...", "Red")
        return

    url = Libs.Networking.fix_url(url)
    if not url:
        themes.set_colored_result(result_text, "url no real :(", "Red")
        return

    headers = {
        "User-Agent": Libs.Networking.get_user_agent()
    }

    themes.set_colored_result(result_text, "getting web info...", "Mauve")
    try:
        res = requests.get(url, headers=headers, allow_redirects=True, stream=True, proxies=Libs.Networking.get_proxies())

        info_text = "found web info :3\n"
        info_text += "=======================\n"

        info_text += web_info_text_thing(res)

        for redirect in res.history:
            info_text += web_info_text_thing(redirect)

        themes.set_colored_result(result_text, info_text, "Mauve")
    except Exception as e:
        console.print(e, style="red")
        themes.set_colored_result(result_text, "thing went boom :(", "Mauve")

def whois_search():
    result_text = "internet.whois_search_result_text"

    domain = dpg.get_value("internet.whois_search_domain_input").strip()
    if not domain:
        themes.set_colored_result(result_text, "you kinda forgot the url...", "Red")
        return

    domain = domain.split("://")[-1].split("/")[0]

    themes.set_colored_result(result_text, "getting whois data...", "Mauve")
    try:
        whois_data = whois.whois(domain)

        whois_text = "got whois data :3\n\n"

        for key, value in whois_data.items():
            if isinstance(value, list):
                whois_text += f"{key.replace('_', ' ')}:\n"
                for thing in value:
                    whois_text += f"{thing}\n"
                whois_text += "\n"
            else:
                whois_text += f"{key.replace('_', ' ')}: {value}\n"

        themes.set_colored_result(result_text, whois_text, "Mauve")

    except Exception as e:
        themes.set_colored_result(result_text, "thing went boom :(", "Red")
        console.print(e, style="red")

def email_scrapper():
    result_text = "internet.email_scrapper_result_text"

    url = dpg.get_value("internet.email_scrapper_url_input").strip()
    if not url:
        themes.set_colored_result(result_text, "you kinda forgot the url...", "Red")
        return

    url = Libs.Networking.fix_url(url)
    if not url:
        themes.set_colored_result(result_text, "url no real :(", "Red")
        return

    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"

    themes.set_colored_result(result_text, f"finding emails...", "Mauve")
    try:
        res = requests.get(url, headers={"User-Agent": Libs.Networking.get_user_agent()}, allow_redirects=True)
        if res.status_code == 404:
            themes.set_colored_result(result_text, "url no found :(", "Red")
            return
        res.raise_for_status()

        matches = re.findall(email_regex, res.text)
        if matches:
            themes.set_colored_result(result_text, f"found emails :3\n{'\n'.join(matches)}", "Mauve")
        else:
            themes.set_colored_result(result_text, "emails no found :(", "Red")
    except Exception as e:
        console.print(e, style="red")
        themes.set_colored_result(result_text, "thing went boom", "Red")

def get_robots_txt():
    result_text = "internet.get_robots_txt_result_text"

    domain = dpg.get_value("internet.get_robots_txt_url_input").strip()
    if not domain:
        themes.set_colored_result(result_text, "you kinda forgot the url...", "Red")
        return

    domain = domain.split("://")[-1].split("/")[0]

    res = requests.get(f"https://{domain}/robots.txt")
    if res.status_code == 404:
        themes.set_colored_result(result_text, "thing no exist", "Red")
        return

    res.raise_for_status()

    themes.set_colored_result(result_text, f"found robots.txt :3\n{res.text}", "Mauve")

def get_all_cert_data():
    result_text = "internet.get_all_cert_data_result_text"

    domain = dpg.get_value("internet.get_all_cert_data_domain_input").strip()
    if not domain:
        themes.set_colored_result(result_text, "you kinda forgot the domain...", "Red")
        return

    domain = domain.split("://")[-1].split("/")[0]

    themes.set_colored_result(result_text, "finding cert info...\ncrt.sh takes a bit :3", "Mauve")


    params = {
        "q": domain,
        "output": "json"
    }
    res = requests.get("https://crt.sh", params=params)
    data = res.json()
    if not data:
        themes.set_colored_result(result_text, "cert no found :(", "Red")
    else:
        info_text = f"{len(data)} certs found :3\n\n"
        info_text += "======================================================\n"
        for thing in data:
            info_text += f"CA Issuer ID: {thing.get('issuer_ca_id', 'N/a')}\n"
            info_text += f"Issuer Name: {thing.get('issuer_name', 'N/a')}\n"
            info_text += f"Common Name: {thing.get('common_name', 'N/a')}\n"
            info_text += f"Name Value: {thing.get('name_value', 'N/a')}\n"
            info_text += f"ID: {thing.get('id', 'N/a')}\n"
            info_text += f"Entry Timestamp: {thing.get('entry_timestamp', 'N/a')}\n"
            info_text += f"Not Before: {thing.get('not_before', 'N/a')}\n"
            info_text += f"Not After: {thing.get('not_after', 'N/a')}\n"
            info_text += f"Serial Number: {thing.get('serial_number', 'N/a')}\n"
            info_text += f"Result Count: {thing.get('result_count', 'N/a')}\n"
            info_text += "======================================================\n\n"
        themes.set_colored_result(result_text, info_text, "Mauve")

def get_current_cert_data():
    result_text = "internet.get_current_cert_data_result_text"

    domain = dpg.get_value("internet.get_current_cert_data_domain_input").strip()
    if not domain:
        themes.set_colored_result(result_text, "you kinda forgot the domain...", "Red")
        return

    domain = domain.split("://")[-1].split("/")[0]

    themes.set_colored_result(result_text, "finding cert info...", "Mauve")