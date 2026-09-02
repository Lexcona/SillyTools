import json
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
import jsbeautifier
import requests
import bs4

from dns.exception import DNSException
from bs4 import BeautifulSoup, Tag
from requests.structures import CaseInsensitiveDict

import Libs.General
import Libs.Networking

import themes

from cryptography import x509
from cryptography.x509.oid import NameOID, ExtensionOID

from Libs.ConfigManager import config

from Vars.General import console, default_error_result_text

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
            themes.set_colored_result(result_text, default_error_result_text, "Red")

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
        themes.set_colored_result(result_text, default_error_result_text, "Red")
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

IMAGE_EXTS = {"png", "jpg", "jpeg", "gif", "svg", "webp", "ico", "bmp", "avif", "tif", "tiff"}
AUDIO_EXTS = {"mp3", "wav", "ogg", "flac", "m4a", "aac", "wma", "opus", "mid", "midi"}
VIDEO_EXTS = {"mp4", "webm", "mkv", "mov", "avi", "m4v", "ogv"}
SCRIPT_EXTS = {"js", "mjs", "cjs"}
STYLE_EXTS = {"css"}
PAGE_EXTS = {"html", "htm", "php", "asp", "aspx", "jsp", "cgi"}

PATH_EXTS = IMAGE_EXTS | AUDIO_EXTS | VIDEO_EXTS | SCRIPT_EXTS | STYLE_EXTS | PAGE_EXTS | {
    "json", "xml", "woff", "woff2", "ttf", "eot", "otf", "pdf", "map", "txt", "wasm", "csv", "zip", "gz"
}

MIME_RE = re.compile(
    r"^(text|application|image|audio|video|font|multipart|model|message)/[\w.+-]+$",
    re.I,
)

JS_IDENT = r"[A-Za-z_$][\w$]*"

def is_valid_path(link: str) -> bool:
    if not link:
        return False

    link = link.strip()
    if len(link) < 2 or len(link) > 2048:
        return False

    if link.startswith(("#", "data:", "javascript:", "mailto:", "tel:", "blob:", "ws:", "wss:")):
        return False

    if MIME_RE.match(link):
        return False

    if re.search(r"[\s<>\\|^*]", link):
        return False

    if "${" in link or "{{" in link or "}}" in link:
        return False

    if re.match(r"https?://", link, re.I) or link.startswith("//"):
        parsed = urllib.parse.urlparse(link if "://" in link else "http:" + link)
        return bool(parsed.netloc)

    if link.startswith(("/", "./", "../")):
        if link in ("/", "./", "../", ".."):
            return False
        return bool(re.search(r"[A-Za-z0-9]", link))

    path_only = link.split("?")[0].split("#")[0]
    filename = path_only.rsplit("/", 1)[-1]
    if "." in filename:
        ext = filename.rsplit(".", 1)[-1].lower()
        if ext in PATH_EXTS:
            return True

    if "/" in path_only and re.match(r"^[\w.-]+(?:/[\w.-]+)+/?$", path_only):
        return True

    return False

def is_base_var(value: str) -> bool:
    if not value:
        return False
    value = value.strip()
    return value.startswith(("http://", "https://", "/", "./", "../", "//"))

def beautify_js(code: str) -> str:
    if not code:
        return ""
    try:
        opts = jsbeautifier.default_options()
        opts.unescape_strings = True
        return jsbeautifier.beautify(code, opts)
    except Exception:
        return code

def url_ext(url: str) -> str:
    path = urllib.parse.urlparse(url).path.lower()
    filename = path.rsplit("/", 1)[-1]
    if "." not in filename:
        return ""
    return filename.rsplit(".", 1)[-1]

def classify_js_url(url: str) -> str:
    ext = url_ext(url)
    if ext in SCRIPT_EXTS:
        return "script"
    if ext in STYLE_EXTS:
        return "stylesheet"
    if ext in IMAGE_EXTS:
        return "image"
    if ext in VIDEO_EXTS:
        return "video"
    if ext in AUDIO_EXTS:
        return "audio"
    return "page"

def kind_from_content_type(url: str, content_type: str) -> str:
    ct = (content_type or "").lower().split(";")[0].strip()
    if ct.startswith("audio/") or ct in ("application/ogg", "application/x-mpegurl"):
        return "audio"
    if ct.startswith("image/"):
        return "image"
    if ct.startswith("video/"):
        return "video"
    if "javascript" in ct or "ecmascript" in ct:
        return "script"
    if "css" in ct:
        return "stylesheet"
    if "json" in ct or ct in ("application/graphql", "application/xml", "text/xml"):
        return "api"
    if "html" in ct:
        return "page"
    return classify_js_url(url)

def is_clean_url(url: str) -> bool:
    if not url:
        return False
    if "{{" in url or "}}" in url:
        return False
    parsed = urllib.parse.urlparse(url)
    if not parsed.netloc or not parsed.hostname:
        return False
    if re.search(r"[)\]'\"={;]", parsed.netloc) or re.search(r"[)\]'\"={;]", parsed.path or ""):
        return False
    path = parsed.path or "/"
    if path in ("/.html", "/.js", "/.css", "/.htm"):
        return False
    parts = [p for p in path.split("/") if p]
    if parts and all(re.fullmatch(r"\d+", p) for p in parts):
        return False
    return True

def empty_cats():
    return {
        "page": set(),
        "image": set(),
        "video": set(),
        "audio": set(),
        "script": set(),
        "stylesheet": set(),
        "iframe": set(),
        "other": set(),
        "api": set(),
        "variable": set()
    }

def format_grouped_urls(urls):
    groups = {}
    for url in urls:
        parsed = urllib.parse.urlparse(url)
        path = parsed.path or "/"
        if path.endswith("/"):
            folder, name = path, ""
        else:
            folder, name = path.rsplit("/", 1)[0] + "/", path.rsplit("/", 1)[-1]
        if parsed.query:
            name = f"{name}?{parsed.query}" if name else f"?{parsed.query}"
        key = f"{parsed.scheme}://{parsed.netloc}{folder}"
        groups.setdefault(key, []).append(name or "/")

    lines = []
    for folder in sorted(groups):
        names = sorted(set(groups[folder]))
        if len(names) == 1:
            lines.append(f"  {folder}{names[0]}")
            continue
        lines.append(f"  {folder} ({len(names)})")
        for name in names:
            lines.append(f"    {name}")
    return lines

def format_api_hits(hits, extra_urls=None):
    by_url = {}
    for hit in hits:
        by_url.setdefault(hit["url"], []).append(hit)

    lines = []
    for url in sorted(by_url):
        lines.append(f"  {url}")
        seen = set()
        for hit in by_url[url]:
            call = re.sub(r"\s+", " ", hit.get("call") or "").strip()
            loc = hit.get("js") or ""
            if hit.get("line"):
                loc = f"{loc}:{hit['line']}"
            key = (call, loc)
            if key in seen:
                continue
            seen.add(key)
            method = hit.get("method") or ""
            if method:
                lines.append(f"    {method} {call}")
            else:
                lines.append(f"    {call}")
            if loc:
                lines.append(f"    {loc}")
    extra_urls = extra_urls or set()
    for url in sorted(extra_urls):
        if url not in by_url:
            lines.append(f"  {url}")
    return lines

def format_mapper_output(all_cats, count_thing, api_hits=None):
    cat_order = ["page", "script", "api", "stylesheet", "iframe", "audio", "video", "image", "other", "variable"]
    group_cats = {"image", "audio", "video"}
    total = sum(len(vals) for key, vals in all_cats.items() if key != "variable")
    lines = [
        f"crawled {count_thing} pages",
        f"found {total} urls",
        ""
    ]
    for cat in cat_order:
        urls = all_cats.get(cat) or set()
        if not urls and not (cat == "api" and api_hits):
            continue
        count = len(urls) if urls else len({h["url"] for h in (api_hits or [])})
        lines.append(f"{cat} ({count}):")
        if cat == "api":
            lines.extend(format_api_hits(api_hits or [], urls))
        elif cat in group_cats:
            lines.extend(format_grouped_urls(urls))
        else:
            for item in sorted(urls):
                lines.append(f"  {item}")
        lines.append("")
    return "\n".join(lines).strip()

def origin_of(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}/"

def host_of(url: str) -> str:
    host = urllib.parse.urlparse(url).hostname or ""
    return host.lower().rstrip(".")

def base_domain(url: str) -> str:
    host = host_of(url)
    if host.startswith("www."):
        host = host[4:]
    return host

def same_site(url: str, root: str) -> bool:
    host = host_of(url)
    if not host or not root:
        return False
    if host.startswith("www."):
        host = host[4:]
    return host == root or host.endswith("." + root)

def extract_js_variables(code: str) -> dict:
    found = {}
    patterns = (
        re.compile(rf"(?:(?:var|let|const)\s+)?({JS_IDENT})\s*=\s*(['\"])(.*?)\2", re.S),
        re.compile(rf"(?:^|[\s{{,])({JS_IDENT})\s*:\s*(['\"])(.*?)\2"),
    )
    for rx in patterns:
        for match in rx.finditer(code):
            name = match.group(1)
            val = match.group(3)
            if is_base_var(val) and is_valid_path(val):
                found.setdefault(name, set()).add(val)
    return found

def subst_templates(text: str, variables: dict) -> list:
    names = list(dict.fromkeys(re.findall(rf"\$\{{({JS_IDENT})\}}", text)))
    if not names:
        return [text]

    unresolved = [name for name in names if not variables.get(name)]
    if unresolved:
        return []

    resolved = [text]
    for name in names:
        next_resolved = []
        for item in resolved:
            for val in variables[name]:
                next_resolved.append(item.replace(f"${{{name}}}", val))
        resolved = next_resolved
        if len(resolved) > 32:
            break
    return resolved

CALL_START = re.compile(
    r"(?:"
    r"\bfetch\s*\("
    r"|\baxios\s*\.\s*(?:get|post|put|patch|delete|request|head)\s*\("
    r"|\baxios\s*\("
    r"|(?:\$|jQuery)\s*\.\s*(?:ajax|get|post|getJSON|put|delete)\s*\("
    r"|\.open\s*\("
    r"|\bsendBeacon\s*\("
    r"|\bnew\s+Request\s*\("
    r")",
    re.I,
)

def matching_paren(code: str, open_idx: int) -> int:
    depth = 0
    in_str = None
    escape = False
    i = open_idx
    while i < len(code):
        c = code[i]
        if in_str:
            if escape:
                escape = False
            elif c == "\\":
                escape = True
            elif c == in_str:
                in_str = None
        elif c in ("'", '"', "`"):
            in_str = c
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1

def call_method(snippet: str) -> str:
    match = re.search(r"""method\s*:\s*['"](\w+)['"]""", snippet, re.I)
    if match:
        return match.group(1).upper()
    match = re.search(r"""\.open\s*\(\s*['"](\w+)['"]""", snippet, re.I)
    if match:
        return match.group(1).upper()
    match = re.search(r"axios\s*\.\s*(get|post|put|patch|delete|head)\s*\(", snippet, re.I)
    if match:
        return match.group(1).upper()
    match = re.search(r"(?:\$|jQuery)\s*\.\s*(get|post|put|delete|getJSON)\s*\(", snippet, re.I)
    if match:
        name = match.group(1).lower()
        if name == "getjson":
            return "GET"
        return name.upper()
    if re.search(r"\bsendBeacon\s*\(", snippet, re.I):
        return "POST"
    return "GET"

def looks_like_api(url: str) -> bool:
    path = urllib.parse.urlparse(url).path.lower()
    if re.search(r"/(api|graphql|rest|json)(/|$)|/v\d+/", path):
        return True
    return url_ext(url) in {"json", "xml"}

def js_source_label(base_url: str) -> str:
    if url_ext(base_url) in SCRIPT_EXTS:
        return base_url
    return f"{base_url} (inline)"

def extract_api_calls(code: str, base_url: str, variables: dict):
    hits = []
    origin = origin_of(base_url)
    js_label = js_source_label(base_url)

    def resolve_raw(raw):
        if not raw or not is_valid_path(raw):
            return None
        link = url_clean(origin, raw.strip())
        if not link or not is_clean_url(link):
            return None
        if classify_js_url(link) in ("image", "audio", "video", "script", "stylesheet"):
            return None
        if url_ext(link) in PAGE_EXTS:
            return None
        return link

    for match in CALL_START.finditer(code):
        close_idx = matching_paren(code, match.end() - 1)
        if close_idx < 0:
            continue
        snippet = code[match.start():close_idx + 1]
        if re.match(r"\.open\s*\(", snippet, re.I):
            if not re.search(r"""open\s*\(\s*['"](?:GET|POST|PUT|PATCH|DELETE|HEAD)['"]""", snippet, re.I):
                continue
        compact = re.sub(r"\s+", " ", snippet).strip()
        if len(compact) > 240:
            compact = compact[:237] + "..."
        line = code[:match.start()].count("\n") + 1
        method = call_method(snippet)
        found_links = set()

        for smatch in re.finditer(r"""(['"])(.*?)\1""", snippet, re.S):
            link = resolve_raw(smatch.group(2))
            if link:
                found_links.add(link)

        for smatch in re.finditer(r"`([^`]*)`", snippet, re.S):
            inner = smatch.group(1)
            for resolved in subst_templates(inner, variables):
                link = resolve_raw(resolved)
                if link:
                    found_links.add(link)
            static_match = re.match(rf"\$\{{({JS_IDENT})\}}(/.+)", inner)
            if static_match:
                link = resolve_raw(static_match.group(2))
                if link:
                    found_links.add(link)

        for cmatch in re.finditer(rf"({JS_IDENT})\s*\+\s*(['\"])(.*?)\2", snippet, re.S):
            name, lit = cmatch.group(1), cmatch.group(3)
            for val in variables.get(name, []):
                link = resolve_raw(val + lit)
                if link:
                    found_links.add(link)

        for link in found_links:
            hits.append({
                "url": link,
                "js": js_label,
                "line": line,
                "call": compact,
                "method": method,
            })
    return hits

def parse_js(code: str, base_url: str, variables: dict):
    candidates = set()
    found_vars = {}
    api_found = []
    if not code:
        return candidates, found_vars, api_found

    code = beautify_js(code)
    found_vars = extract_js_variables(code)
    merged = {key: set(val) for key, val in variables.items()}
    for name, vals in found_vars.items():
        merged.setdefault(name, set()).update(vals)

    origin = origin_of(base_url)
    api_found = extract_api_calls(code, base_url, merged)

    def add_link(raw):
        if not raw or not is_valid_path(raw):
            return
        link = url_clean(origin, raw.strip())
        if link and is_clean_url(link):
            candidates.add(link)

    for match in re.finditer(r"""(['"])(.*?)\1""", code, re.S):
        add_link(match.group(2))

    for match in re.finditer(r"`([^`]*)`", code, re.S):
        inner = match.group(1)
        for resolved in subst_templates(inner, merged):
            add_link(resolved)

        static_match = re.match(rf"\$\{{({JS_IDENT})\}}(/.+)", inner)
        if static_match:
            add_link(static_match.group(2))

        for var_match in re.finditer(rf"\$\{{({JS_IDENT})\}}", inner):
            name = var_match.group(1)
            for val in merged.get(name, []):
                add_link(inner.replace(f"${{{name}}}", val))

    for match in re.finditer(rf"({JS_IDENT})\s*\+\s*(['\"])(.*?)\2", code, re.S):
        name, lit = match.group(1), match.group(3)
        for val in merged.get(name, []):
            add_link(val + lit)

    for match in re.finditer(rf"(['\"])(.*?)\1\s*\+\s*({JS_IDENT})", code, re.S):
        lit, name = match.group(2), match.group(3)
        for val in merged.get(name, []):
            add_link(lit + val)

    return candidates, found_vars, api_found

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

    url_part = url_part.strip()
    file_kind = classify_js_url(url_part if "://" in url_part else f"http://x/{url_part.lstrip('/')}")
    if file_kind in ("image", "audio", "video", "script", "stylesheet"):
        kind = file_kind
    return url_part, kind


def site_mapper(sender, app_data, user_data):
    max_threads = 16
    timeout = 10
    result_widget = "internet.site_mapper_result_text"

    url = dpg.get_value("internet.site_mapper_domain_input").strip()
    if not url:
        themes.set_colored_result(result_widget, "you kinda forgot the url...", "Red")
        return

    start_url = Libs.Networking.fix_url(url)
    root = base_domain(start_url)

    session = requests.Session()
    session.headers["User-Agent"] = Libs.Networking.get_user_agent()
    session.proxies = Libs.Networking.get_proxies()

    did_urls = set()
    queue = [start_url]
    found_urls = {start_url}

    all_cats = empty_cats()

    lock = threading.Lock()
    shared_vars = {}
    exist_cache = {}
    js_pending = set()
    count_thing = 0

    themes.set_colored_result(result_widget, f"crawling from {start_url}...", "Mauve")

    def probe_url(link):
        with lock:
            cached = exist_cache.get(link)
        if cached is not None:
            return cached

        result = (False, None)
        try:
            res = session.head(link, timeout=timeout, allow_redirects=True)
            if res.status_code in (403, 405, 501):
                res = session.get(link, timeout=timeout, allow_redirects=True, stream=True)
                res.close()
            if 200 <= res.status_code < 400:
                result = (True, kind_from_content_type(link, res.headers.get("content-type", "")))
        except Exception:
            result = (False, None)

        with lock:
            exist_cache[link] = result
        return result

    def take_js_vars(found_vars, cats):
        with lock:
            for name, vals in found_vars.items():
                shared_vars.setdefault(name, set()).update(vals)
                for val in vals:
                    if is_valid_path(val) and "{{" not in val and "}}" not in val:
                        cats["variable"].add(f"{name} = {val}")

    def remember_js(candidates):
        for link in candidates:
            if same_site(link, root):
                with lock:
                    js_pending.add(link)

    def fetch_and_parse(url):
        try:
            res = session.get(url, timeout=timeout, allow_redirects=True)
            if res.status_code == 404:
                return url, set(), empty_cats()
            res.raise_for_status()

            ct = res.headers.get("content-type", "").lower()
            path = urllib.parse.urlparse(url).path.lower()
            is_js = "javascript" in ct or "ecmascript" in ct or path.endswith((".js", ".mjs", ".cjs"))
            is_html = "text/html" in ct or res.text.lstrip()[:15].lower().startswith(("<!doctype", "<html"))

            new_pages = set()
            cats = empty_cats()

            with lock:
                vars_snap = {key: set(val) for key, val in shared_vars.items()}

            if is_js:
                candidates, found_vars = parse_js(res.text, url, vars_snap)
                take_js_vars(found_vars, cats)
                remember_js(candidates)
                return url, new_pages, cats

            if not is_html:
                kind = kind_from_content_type(url, ct)
                cats[kind].add(url)
                return url, set(), cats

            soup = BeautifulSoup(res.text, "html.parser")

            for tag in soup.find_all():
                link_text, kind = classify_tag(tag)

                if link_text:
                    link = url_clean(url, link_text)

                    if link and is_clean_url(link):
                        if kind in cats:
                            cats[kind].add(link)

                        if kind in ("page", "script") and same_site(link, root):
                            new_pages.add(link)

                if tag.name == "script" and not tag.get("src"):
                    script_text = tag.get_text()
                    if script_text and script_text.strip():
                        candidates, found_vars = parse_js(script_text, url, vars_snap)
                        take_js_vars(found_vars, cats)
                        remember_js(candidates)
                        for name, vals in found_vars.items():
                            vars_snap.setdefault(name, set()).update(vals)

            return url, new_pages, cats

        except Exception as e:
            console.print(e, style="red")
            return url, set(), empty_cats()

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

        pending = list(js_pending)
        if pending:
            themes.set_colored_result(result_widget, f"checking {len(pending)} js urls...", "Mauve")

            def probe_pair(link):
                exists, kind = probe_url(link)
                return link, exists, kind

            extra_pages = []
            checked = 0
            for future in concurrent.futures.as_completed([executor.submit(probe_pair, link) for link in pending]):
                link, exists, kind = future.result()
                checked += 1
                if checked % 25 == 0 or checked == len(pending):
                    themes.set_colored_result(result_widget, f"checked js urls: {checked}/{len(pending)}", "Mauve")
                if not exists or not kind:
                    continue
                with lock:
                    all_cats[kind].add(link)
                if kind in ("page", "script") and same_site(link, root) and link not in found_urls:
                    extra_pages.append(link)

            for page in extra_pages:
                if page not in found_urls:
                    found_urls.add(page)
                    queue.append(page)

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

    themes.set_colored_result(result_widget, format_mapper_output(all_cats, count_thing), "Mauve")

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
        themes.set_colored_result(result_text, default_error_result_text, "Red")
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
    if res.raw._connection and res.raw._connection.sock:
        ip_addr = res.raw._connection.sock.getpeername()[0]
        info_text += f"ip: {ip_addr} {Libs.Networking.service_tag(ip_addr)}\n"
    info_text += f"status code: {res.status_code}\n"
    info_text += f"server: {res.headers.get('server', 'unknown')}\n"
    info_text += f"\nheaders:\n"
    for key, value in clean_headers(res.headers).items():
        info_text += f"{key}: {Libs.General.dict_to_pretty_str(value)}\n"
    info_text += "\ncookies:\n"
    for key, value in res.cookies.items():
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
        themes.set_colored_result(result_text, default_error_result_text, "Mauve")

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
        themes.set_colored_result(result_text, default_error_result_text, "Red")
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
        res = requests.get(url, headers={"User-Agent": Libs.Networking.get_user_agent()}, allow_redirects=True, proxies=Libs.Networking.get_proxies())
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
        themes.set_colored_result(result_text, default_error_result_text, "Red")

def get_robots_txt():
    result_text = "internet.get_robots_txt_result_text"

    domain = dpg.get_value("internet.get_robots_txt_url_input").strip()
    if not domain:
        themes.set_colored_result(result_text, "you kinda forgot the url...", "Red")
        return

    domain = domain.split("://")[-1].split("/")[0]
    try:
        res = requests.get(f"https://{domain}/robots.txt", proxies=Libs.Networking.get_proxies())
        if res.status_code == 404:
            themes.set_colored_result(result_text, "thing no exist", "Red")
            return

        res.raise_for_status()

        themes.set_colored_result(result_text, f"found robots.txt :3\n{res.text}", "Mauve")
    except Exception as e:
        themes.set_colored_result(result_text, default_error_result_text, "Red")
        console.print(e, style="red")
        return

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
    try:
        res = requests.get("https://crt.sh", params=params, proxies=Libs.Networking.get_proxies())
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
    except Exception as e:
        themes.set_colored_result(result_text, default_error_result_text, "Red")
        console.print(e, style="red")
        return

def get_current_cert_data():
    result_text = "internet.get_current_cert_data_result_text"

    domain = dpg.get_value("internet.get_current_cert_data_domain_input").strip()
    if not domain:
        themes.set_colored_result(result_text, "you kinda forgot the domain...", "Red")
        return

    domain = domain.split("://")[-1].split("/")[0]

    themes.set_colored_result(result_text, "finding cert info...", "Mauve")

    if ":" in domain:
        ip_addr_split = domain.split(":")
        ip_addr = ip_addr_split[0]
        port = ip_addr_split[-1]
    else:
        ip_addr = domain
        port = 443

    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_OPTIONAL

    info_text = "found cert data :3\n"
    try:
        cert_data = Libs.Networking.get_cert(ip_addr, port)
        if cert_data["connection"].get("error"):
            themes.set_colored_result(result_text, default_error_result_text, "Red")
            console.print(cert_data["connection"]["error"], style="red")
            return

        cert = cert_data.get("certificate", {})
        print(json.dumps(cert_data, indent=4))
        if cert:
            info_text += Libs.General.dict_to_pretty_str(cert_data)
            themes.set_colored_result(result_text, info_text, "Mauve")
        else:
            themes.set_colored_result(result_text, "cert no found :(", "Red")
    except Exception as e:
        themes.set_colored_result(result_text, default_error_result_text, "Red")
        console.print(e, style="red")