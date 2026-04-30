import socks
import random
import socket
import requests
import ipaddress
import urllib.parse

from Libs.ConfigManager import config
from contextlib import contextmanager

from Vars.General import console

user_agents = []

cloudflare_ips = []
github_ips = []

def get_ipinfo(ip:str, token:str=None, format:bool=False):
    # this is the free, accountless api
    # works for seeing if an api exists without a token
    res = requests.get(f"https://ipinfo.io/{ip}/json", proxies=get_proxies())
    data = res.json()
    if res.status_code == 404 or data.get("bogon"):
        return False
    res.raise_for_status()

    # ipinfo.io has a crappy geolocation system, and this one is better
    res_geo = requests.get(f"https://geolocation-db.com/json/{ip}", proxies=get_proxies())
    res_geo.raise_for_status()
    geo_data = res_geo.json()

    # also because the last api doesn't have timezones we use this
    res_timezone = requests.get(f"https://timeapi.io/api/v1/timezone/coordinate", params={"latitude": geo_data["latitude"], "longitude": geo_data["longitude"]}, proxies=get_proxies())
    res_geo.raise_for_status()
    timezone_data = res_timezone.json()

    is_tokener = False
    if token:
        if token.replace(" ", "") != "":
            is_tokener = True

    if is_tokener:
        if format == False:
            return res.json()
        ip_text = ""
        if data.get("ip"):
            ip_text += "IP: "+data.get("ip")+"\n"
        if data.get("hostname"):
            ip_text += "Hostname: "+data.get("hostname")+"\n"
        if data.get("org"):
            ip_text += "ISP: "+data.get("org")+"\n"

        ip_text += "\n"
        if geo_data.get("latitude"):
            ip_text += "Coords: " + str(geo_data.get("latitude")) + ", " + str(geo_data.get("longitude")) + "\n"
        if geo_data.get("city"):
            ip_text += "Location: "+geo_data.get("city", "Unknown")+", "+geo_data.get("state", "Unknown")+"\n"
        if geo_data.get("postal"):
            ip_text += "Zip Code/Postal: "+geo_data.get("postal")+"\n"
        if geo_data.get("country_name"):
            ip_text += "Country: " + geo_data.get("country_name") + " (" + geo_data.get("country_code") + ")" + "\n"
        if timezone_data.get("timezone"):
            ip_text += "Timezone: " + timezone_data.get("timezone") + "\n"
        return ip_text
    else:
        res = requests.get(f"https://api.ipinfo.io/lookup/{ip}?token={token}", proxies=get_proxies())
        data = res.json()

        # since ipinfo.io doesn't have a thing to find the plan, we have to do this.
        if res.status_code == 403:
            res = requests.get(f"https://api.ipinfo.io/lite/{ip}?token={token}", proxies=get_proxies())
            data = res.json()
            if res.status_code == 404 or data.get("bogon"):
                return False
            res.raise_for_status()

            if not format:
                return res.json()
            else:
                ip_text = ""
                if data.get("ip"):
                    ip_text += "IP: " + data.get("ip") + "\n"
                if data.get("as_name"):
                    ip_text += "AS Name: " + data.get("as_name") + "\n"
                if data.get("asn"):
                    ip_text += "ASN: " + data.get("asn") + "\n"
                if data.get("as_domain"):
                    ip_text += "AS Domain: " + data.get("as_domain") + "\n"

                ip_text += "\n"

                if geo_data.get("latitude"):
                    ip_text += "Coords: " + str(geo_data.get("latitude")) + ", " + str(geo_data.get("longitude")) + "\n"
                if geo_data.get("city"):
                    ip_text += "Location: " + geo_data.get("city", "Unknown") + ", " + geo_data.get("state", "Unknown") + "\n"
                if geo_data.get("postal"):
                    ip_text += "Zip Code/Postal: " + geo_data.get("postal") + "\n"
                if geo_data.get("country_name"):
                    ip_text += "Country: " + geo_data.get("country_name") + " (" + geo_data.get("country_code") + ")" + "\n"
                if timezone_data.get("timezone"):
                    ip_text += "Timezone: " + timezone_data.get("timezone") + "\n"
                return ip_text
        res.raise_for_status()
        if not format:
            return res.json()

        # I haven't tested this part, since I am not paying 49$ for this
        ip_text = ""
        if data.get("ip"):
            ip_text += "IP: "+data.get("ip")+"\n"
        if data.get("hostname"):
            ip_text += "Hostname: "+data.get("hostname")+"\n"

        ip_text += "\n"

        if geo_data.get("latitude"):
            ip_text += "Coords: " + str(geo_data.get("latitude")) + ", " + str(geo_data.get("longitude")) + "\n"
        if geo_data.get("city"):
            ip_text += "Location: " + geo_data.get("city", "Unknown") + ", " + geo_data.get("state", "Unknown") + "\n"
        if geo_data.get("postal"):
            ip_text += "Zip Code/Postal: " + geo_data.get("postal") + "\n"
        if geo_data.get("country_name"):
            ip_text += "Country: " + geo_data.get("country_name") + " (" + geo_data.get("country_code") + ")" + "\n"
        if timezone_data.get("timezone"):
            ip_text += "Timezone: " + timezone_data.get("timezone") + "\n"

        ip_text += "\n"

        asn = data.get("as")
        if asn:
            if asn.get("asn"):
                ip_text += "ASN: " + asn.get("asn") + "\n"
            if asn.get("name"):
                ip_text += "Name: " + asn.get("name") + "\n"
            if asn.get("domain"):
                ip_text += "Domain: " + asn.get("domain") + "\n"
            if asn.get("type"):
                ip_text += "Type: " + asn.get("type") + "\n"
            if asn.get("last_changed"):
                ip_text += "Last Changed: " + asn.get("last_changed") + "\n"

        ip_text += "\n"

        mobile = data.get("mobile")
        if mobile:
            if mobile.get("name"):
                ip_text += "Name: " + mobile.get("name") + "\n"
            if mobile.get("mcc"):
                ip_text += "MCC: " + mobile.get("mcc") + "\n"
            if mobile.get("mnc"):
                ip_text += "MNC: " + mobile.get("mnc") + "\n"

        ip_text += "\n"

        anonymous = data.get("anonymous")
        if anonymous:
            if anonymous.get("is_proxy"):
                ip_text += "Is Proxy: " + anonymous.get("is_proxy") + "\n"
            if anonymous.get("is_relay"):
                ip_text += "Is Relay: " + anonymous.get("is_relay") + "\n"
            if anonymous.get("is_tor"):
                ip_text += "Is Tor: " + anonymous.get("is_tor") + "\n"
            if anonymous.get("is_vpn"):
                ip_text += "Is VPN: " + anonymous.get("is_vpn") + "\n"
            if anonymous.get("is_res_proxy"):
                ip_text += "Is RES Proxy: " + anonymous.get("is_res_proxy") + "\n"

        ip_text += "\n"
        if data.get("is_anonymous"):
            ip_text += "Is Anonymous: " + data.get("is_anonymous") + "\n"
        if data.get("is_anycast"):
            ip_text += "Is Anycast: " + data.get("is_anycast") + "\n"
        if data.get("is_hosting"):
            ip_text += "Is Hosting: " + data.get("is_hosting") + "\n"
        if data.get("is_mobile"):
            ip_text += "Is Mobile: " + data.get("is_mobile") + "\n"
        if data.get("is_satellite"):
            ip_text += "Is Satellite: " + data.get("is_satellite") + "\n"
        return ip_text

def get_cloudflare_ips():
    global cloudflare_ips

    # better to cache since it's faster
    if cloudflare_ips:
        return cloudflare_ips

    ips = []

    try:
        ip_text = ""

        # first we get the ipv4
        res_v4 = requests.get("https://www.cloudflare.com/ips-v4", proxies=get_proxies())
        res_v4.raise_for_status()
        ip_text += f"{res_v4.text}\n"

        # then the ipv6
        res_v6 = requests.get("https://www.cloudflare.com/ips-v6", proxies=get_proxies())
        res_v6.raise_for_status()
        ip_text += f"{res_v6.text}"

        # then with both of them combined together, we only need to parse once
        for ip in ip_text.strip().splitlines():
            ip = ip.strip()

            # simple check to see if it's an empty string or comment
            # even though I don't think I have seen comments in the api
            if ip and not ip.startswith('#'):
                ips.append(ipaddress.ip_network(ip))

        # caching for later just in case, also dupe removing.
        cloudflare_ips = list(set(ips))
    except Exception as e:
        console.print(e, style="red")
        cloudflare_ips = []

    return cloudflare_ips

def get_github_ips():
    global github_ips
    if github_ips:
        return github_ips

    try:
        res = requests.get("https://api.github.com/meta", proxies=get_proxies())
        res.raise_for_status()

        # parses through all the github pages ips for detections
        for thing in res.json().get("pages", []):
            github_ips.append(ipaddress.ip_network(thing))

        # just to remove dupes, even though I doubt github would put dupes in an api endpoint.
        github_ips = list(set(github_ips))
    except Exception as e:
        console.print(e, style="red")
    return github_ips

def service_tag(ip:str):
    try:
        ip_thing = ipaddress.ip_address(ip)
    except Exception:
        return ""

    for cidr in get_cloudflare_ips():
        if ip_thing in cidr:
            return "(cloudflare)"

    for cidr in get_github_ips():
        if ip_thing in cidr:
            return "(github pages)"

    return ""

def get_user_agent():
    global user_agents
    if not user_agents:
        #user_agents = requests.get("https://gist.githubusercontent.com/pzb/b4b6f57144aea7827ae4/raw/cf847b76a142955b1410c8bcef3aabe221a63db1/user-agents.txt", proxies=get_proxies()).text.strip().splitlines()
        user_agents = requests.get("https://microlink.io/user-agents.json", proxies=get_proxies()).json()["user"]

    return random.choice(user_agents)

def fix_url(url:str):
    url = url.strip()

    # thing to check for empty strings
    if not url:
        return False

    # fixing the url to have https:// if it doesn't have https or http
    parsed = urllib.parse.urlparse(url)
    if not parsed.scheme:
        url = "https://" + url
    elif parsed.scheme not in ("http", "https"):
        return False

    # extra check, probley useless but good to have to be safe.
    if not parsed.netloc and "://" in url:
        parsed = urllib.parse.urlparse(url)
        if not parsed.netloc:
            return False

    return url

def check_url(url:str):
    url = fix_url(url)
    if url == False:
        return False

    session = requests.session()
    session.proxies = get_proxies()
    session.headers = {
        "User-Agent": get_user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    try:
        try:
            # first we try with a head request, which would get most
            res = session.head(url, timeout=10, allow_redirects=True)
        except requests.exceptions.RequestException:
            # but get is here just to be safe
            res = session.get(url, timeout=10, allow_redirects=True, stream=True)
            res.close()

        if res.status_code == 404:
            return False
        return True
    except requests.exceptions.Timeout:
        return "Timed Out"

    # I didn't know you could use a tuple for this until I found it on stack overflow.
    except (requests.exceptions.InvalidURL, requests.exceptions.ConnectionError, requests.exceptions.TooManyRedirects, requests.exceptions.MissingSchema):
        return False
    except Exception as e:
        console.print(e, style="red")
        return None

def get_local_ip():
    socketer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        socketer.connect(("8.8.8.8", 80))
        return socketer.getsockname()[0]
    except Exception:
        return "Unknown"
    finally:
        socketer.close()

def get_proxies():
    http_proxy   = config.read("proxies/http", "").strip()
    https_proxy  = config.read("proxies/https", "").strip()
    socks5_proxy = config.read("proxies/socks5", "").strip()

    proxies = {}

    if socks5_proxy:
        if socks5_proxy.startswith("socks5://"):
            socks5_proxy = "socks5h://" + socks5_proxy[8:]
        elif not socks5_proxy.startswith("socks5h://"):
            socks5_proxy = "socks5h://" + socks5_proxy.lstrip(":/")

        proxies["http"] = socks5_proxy
        proxies["https"] = socks5_proxy

    else:
        if http_proxy:
            proxies["http"] = http_proxy
        if https_proxy:
            proxies["https"] = https_proxy
        elif http_proxy:
            proxies["https"] = http_proxy

    return proxies

@contextmanager
def proxy_socket(proxies: dict = None):
    if not proxies:
        yield
        return

    proxy_url = proxies.get("http") or proxies.get("https")
    if not proxy_url or not proxy_url.startswith(("socks5://", "socks5h://")):
        yield
        return

    rdns = "socks5h" in proxy_url
    proxy_str = proxy_url.replace("socks5h://", "").replace("socks5://", "")

    if "@" in proxy_str:
        auth, host_port = proxy_str.split("@", 1)
        if ":" in auth:
            username, password = auth.split(":", 1)
        else:
            username, password = (None, None)
    else:
        username = password = None
        host_port = proxy_str

    try:
        host, port = host_port.split(":")
        port = int(port)
    except Exception:
        yield
        return

    original_socket = socket.socket
    original_create_connection = socket.create_connection

    socks.set_default_proxy(
        proxy_type=socks.SOCKS5,
        addr=host,
        port=port,
        username=username,
        password=password,
        rdns=rdns
    )
    socket.socket = socks.socksocket

    def proxied_create_connection(address, timeout=None, source_address=None):
        sock = socks.socksocket()
        if timeout is not None:
            sock.settimeout(timeout)
        if source_address:
            sock.bind(source_address)
        sock.connect(address)
        return sock

    socket.create_connection = proxied_create_connection

    try:
        yield
    finally:
        socket.socket = original_socket
        socket.create_connection = original_create_connection
        socks.set_default_proxy()