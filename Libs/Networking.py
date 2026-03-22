import random
import requests
import ipaddress

from rich.console import Console

console = Console()

user_agents = []
cloudflare_ips = None
GITHUB_PAGES_IPS = {
    ipaddress.ip_network("185.199.108.153/32"),
    ipaddress.ip_network("185.199.109.153/32"),
    ipaddress.ip_network("185.199.110.153/32"),
    ipaddress.ip_network("185.199.111.153/32"),
    ipaddress.ip_network("2606:50c0:8000::153/128"),
    ipaddress.ip_network("2606:50c0:8001::153/128"),
    ipaddress.ip_network("2606:50c0:8002::153/128"),
    ipaddress.ip_network("2606:50c0:8003::153/128"),
}

def get_ipinfo(ip:str, token:str=None, format:bool=False):
    if token == None:
        res = requests.get(f"https://ipinfo.io/{ip}/json")
        data = res.json()
        if res.status_code == 404 or data.get("bogon"):
            return False
        res.raise_for_status()

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
        if data.get("loc"):
            ip_text += "Coords: " + data.get("loc") + "\n"
        if data.get("city"):
            ip_text += "Location: "+data.get("city", "Unknown")+", "+data.get("region", "Unknown")+"\n"
        if data.get("postal"):
            ip_text += "Zip Code/Postal: "+data.get("postal")+"\n"
        if data.get("country"):
            ip_text += "Country: " + data.get("country") + "\n"
        if data.get("timezone"):
            ip_text += "Timezone: " + data.get("timezone") + "\n"
        return ip_text
    else:
        res = requests.get(f"https://api.ipinfo.io/lookup/{ip}?token={token}")
        data = res.json()
        if res.status_code == 404 or data.get("bogon"):
            return False
        if res.status_code == 403:
            res = requests.get(f"https://api.ipinfo.io/lite/{ip}?token={token}")
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

                if data.get("country"):
                    ip_text += "Country: " + data.get("country") + " (" + data.get("country_code") + ")" + "\n"
                if data.get("continent"):
                    ip_text += "Continent: " + data.get("continent") + " (" + data.get("continent_code") + ")" + "\n"
                return ip_text
        res.raise_for_status()
        if not format:
            return res.json()

        ip_text = ""
        if data.get("ip"):
            ip_text += "IP: "+data.get("ip")+"\n"
        if data.get("hostname"):
            ip_text += "Hostname: "+data.get("hostname")+"\n"

        ip_text += "\n"

        geo = data.get("geo")
        if geo:
            if geo.get("latitude"):
                ip_text += "Coords: " + geo.get("latitude")+", "+geo.get("longitude") + "\n"
            if geo.get("city"):
                ip_text += "Location: " + geo.get("city", "Unknown") + ", " + geo.get("region", "Unknown") + " ("+geo.get("region_code", "Unknown") +")" + "\n"
            if geo.get("postal_code"):
                ip_text += "Zip Code/Postal: " + geo.get("postal_code") + "\n"
            if geo.get("country"):
                ip_text += "Country: " + geo.get("country") + " (" + geo.get("country_code") + ")" + "\n"
            if geo.get("continent"):
                ip_text += "Continent: " + geo.get("continent") + " (" + geo.get("continent_code") + ")" + "\n"
            if geo.get("timezone"):
                ip_text += "Timezone: " + geo.get("timezone") + "\n"
            if geo.get("dma_code"):
                ip_text += "DMA Code: " + geo.get("dma_code") + "\n"
            if geo.get("geoname_id"):
                ip_text += "Geoname ID: " + geo.get("geoname_id") + "\n"
            if geo.get("radius"):
                ip_text += "Radius: " + geo.get("radius") + "\n"

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
    if cloudflare_ips is not None:
        return cloudflare_ips

    ips = set()

    try:
        res = requests.get("https://www.cloudflare.com/ips-v4", timeout=8)
        res.raise_for_status()
        for line in res.text.strip().splitlines():
            line = line.strip()
            if line and not line.startswith('#'):
                ips.add(ipaddress.ip_network(line))

        res = requests.get("https://www.cloudflare.com/ips-v6", timeout=8)
        res.raise_for_status()
        for line in res.text.strip().splitlines():
            line = line.strip()
            if line and not line.startswith('#'):
                ips.add(ipaddress.ip_network(line))

        cloudflare_ips = ips
    except Exception as e:
        console.print(e, style="red")
        cloudflare_ips = set()

    return cloudflare_ips

# Yes ths part is GPTed, I was too lazy to find the api and make a function to get all the GitHub page IPs.
def get_github_pages_networks():
    try:
        r = requests.get("https://api.github.com/meta", timeout=5)
        r.raise_for_status()
        data = r.json()
        pages_cidrs = data.get("pages", [])
        return {ipaddress.ip_network(c) for c in pages_cidrs}
    except Exception as e:
        print(f"GitHub meta fetch failed: {e}")
        # Fallback to hardcoded
        return GITHUB_PAGES_IPS

def service_tag(ip:str):
    try:
        ip_thing = ipaddress.ip_address(ip)
    except Exception:
        return ""

    for cidr in get_cloudflare_ips():
        if ip_thing in cidr:
            return "(cloudflare)"

    for cidr in get_github_pages_networks():
        if ip_thing in cidr:
            return "(github pages)"

    return ""

def get_user_agent():
    global user_agents
    if not user_agents:
        user_agents = requests.get("https://gist.githubusercontent.com/pzb/b4b6f57144aea7827ae4/raw/cf847b76a142955b1410c8bcef3aabe221a63db1/user-agents.txt").text.strip().splitlines()

    return random.choice(user_agents)