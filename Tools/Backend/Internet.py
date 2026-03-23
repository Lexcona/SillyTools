import os
import ssl
import time
import socket
import threading
import urllib.parse
import concurrent.futures

from collections import deque
from queue import Queue, Empty

import dearpygui.dearpygui as dpg
import dns.resolver
import pywebcopy
import requests
import bs4

from dns.exception import DNSException
from bs4 import BeautifulSoup

import Libs.Networking

import themes

from cryptography import x509
from rich.console import Console
from cryptography.x509.oid import NameOID, ExtensionOID

from Libs.ConfigManager import config

console = Console()

def search_domain_nameservers(sender, app_data, user_data):
    result_text = "internet.find_name_servers_result_text"

    domain = dpg.get_value("internet.find_name_servers_domain_input").strip()

    if not domain:
        themes.set_colored_result(result_text, "you kinda forgot the domain...", "Red")
        return

    try:
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
        themes.set_colored_result(result_text,f"creating connection at {ip_addr}:{port}...","Mauve")
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
                    cn = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
                    if cn:
                        common_name = cn[0].value
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
                    dns_text += f"admin:    {rdata.rname}\n"
                    dns_text += f"serial:   {rdata.serial}\n"
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

def make_absolute(base_url: str, raw_link: str):
    if not raw_link:
        return None

    if raw_link.startswith(('#', 'data:', 'javascript:', 'mailto:', 'tel:')):
        return None

    try:
        abs_url = urllib.parse.urljoin(base_url, raw_link.strip())
        parsed = urllib.parse.urlparse(abs_url)

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
    url_part = None
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
    result_widget = "internet.site_mapper_result_text"

    raw_input = dpg.get_value("internet.site_mapper_domain_input").strip()
    if not raw_input:
        themes.set_colored_result(result_widget, "you kinda forgot the url...", "Red")
        return

    start_url = raw_input
    if '://' not in start_url and not start_url.startswith('/'):
        start_url = 'https://' + start_url.lstrip()

    parsed = urllib.parse.urlparse(start_url)
    if not parsed.scheme or parsed.scheme not in ('http', 'https'):
        themes.set_colored_result(result_widget, "url no formated correctly :(", "Red")
        return

    start_url = urllib.parse.urlunparse((
        parsed.scheme,
        parsed.netloc.lower(),
        parsed.path or '/',
        parsed.params,
        parsed.query,
        ''
    ))

    MAX_PAGES    = 2000000
    MAX_WORKERS  = 16
    TIMEOUT      = 10

    domain = urllib.parse.urlparse(start_url).netloc

    session = requests.Session()
    session.headers["User-Agent"] = Libs.Networking.get_user_agent()
    session.timeout = TIMEOUT

    visited     = set()
    to_visit    = [start_url]
    discovered  = {start_url}
    all_resources = {
        "page": set(), "image": set(), "video": set(), "audio": set(),
        "script": set(), "stylesheet": set(), "iframe": set(), "other": set(),
    }

    lock = threading.Lock()
    processed_count = 0

    themes.set_colored_result(result_widget, f"starting threaded crawl ({MAX_WORKERS} workers) from {start_url}...", "Mauve")

    def fetch_and_parse(url):
        nonlocal processed_count

        try:
            res = session.get(url)
            res.raise_for_status()

            if "text/html" not in res.headers.get("content-type", "").lower():
                return url, set(), {}

            soup = BeautifulSoup(res.text, "html.parser")

            new_pages = set()
            resources = {
                "page": set(),
                "image": set(),
                "video": set(),
                "audio": set(),
                "script": set(),
                "stylesheet": set(),
                "iframe": set(),
                "other": set(),
            }

            for tag in soup.find_all():
                link_text, kind = classify_tag(tag)
                if not link_text:
                    continue

                abs_link = make_absolute(url, link_text)
                if not abs_link:
                    continue

                link_domain = urllib.parse.urlparse(abs_link).netloc

                if kind in resources:
                    resources[kind].add(abs_link)

                if kind == "page" and link_domain == domain:
                    new_pages.add(abs_link)

            return url, new_pages, resources

        except Exception as e:
            print(f"fetch_and_parse failed for {url}: {type(e).__name__} - {e}")
            return url, set(), {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        while to_visit and processed_count < MAX_PAGES:
            current_batch = []
            batch_size = min(MAX_WORKERS * 2, len(to_visit))

            for _ in range(batch_size):
                if to_visit:
                    url = to_visit.pop(0)
                    if url not in visited:
                        current_batch.append(executor.submit(fetch_and_parse, url))

            if not current_batch:
                break

            for future in concurrent.futures.as_completed(current_batch):
                url, new_pages, res_dict = future.result()

                with lock:
                    if url in visited:
                        continue
                    visited.add(url)
                    processed_count += 1

                    for cat, links in res_dict.items():
                        all_resources[cat].update(links)

                    added_count = 0
                    for p in new_pages:
                        if p not in discovered and p not in visited:
                            discovered.add(p)
                            to_visit.append(p)
                            added_count += 1

                    if processed_count % 5 == 0 or added_count > 0:
                        msg = f"crawled {processed_count} pages | discovered {len(discovered)} urls"
                        if added_count > 0:
                            msg += f" (+{added_count} new)"
                        themes.set_colored_result(result_widget, msg, "Mauve")

    total_found = sum(len(v) for v in all_resources.values())

    summary_lines = []
    summary_lines.append(f"crawled {processed_count} pages")
    summary_lines.append(f"found {total_found} things\n")

    for cat, urls in sorted(all_resources.items(), key=lambda x: -len(x[1])):
        if not urls:
            continue
        count = len(urls)
        summary_lines.append(f"{cat} ({count} found):")
        for ex in sorted(urls):
            summary_lines.append(f"  {ex}")
        summary_lines.append("")

    summary_lines.append("found pages:")
    for u in sorted(visited):
        summary_lines.append(f"  {u}")

    final_text = "\n".join(summary_lines).strip()
    themes.set_colored_result(result_widget, final_text, "Mauve")

def tag_dumper():
    result_text = "internet.tag_dumper_result_text"

    url = dpg.get_value("internet.tag_dumper_url_input").strip()
    if not url:
        themes.set_colored_result(result_text, "you kinda forgot the url...", "Red")
        return

    if not "://" in url:
        url = "https://"+url

    output = dpg.get_value("internet.tag_dumper_output_input").strip()
    if not output:
        output = f"./export/tag_dumper/{url.split('://')[-1].replace('/', '_')}"

    os.makedirs(output, exist_ok=True)

    headers = {
        "User-Agent": Libs.Networking.get_user_agent()
    }

    tag_count = {

    }

    try:
        res = requests.get(url, headers=headers)
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

    if not "://" in url:
        url = "https://"+url

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
        res = requests.request(method, url, allow_redirects=True, headers=headers)

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
        url_check = Libs.Networking.check_url(url)
        if url_check == True:
            themes.set_colored_result(result_text, f"{url} valid :3", "Mauve")
            valid_urls.append(url)
        elif url_check == "Timed Out":
            themes.set_colored_result(result_text, f"{url} timed out :(", "Red")
            timed_urls.append(url)
        else:
            themes.set_colored_result(result_text, f"{url} invalid :(", "Red")
            invalid_urls.append(url)
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

