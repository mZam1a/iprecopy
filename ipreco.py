import argparse
import socket
from typing import Type
import sys
import requests
import ipaddress

#COLORS
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RED = "\033[91m"
RESET = "\033[0m"

#BANNER 
BANNER = r"""
######  ####### ###### #####  ######  ##   ##  
##   ## ##     ###    ##   ## ##   ## ##   ##  
######  ###### ##     ##   ## ######   #####   
##  ##  ##     ###    ##   ## ##         ##    
##   ## ####### ###### #####  ##         ##    
"""

#GLOBAL
URL = "https://ip.guide/"

def pointers(COLOR):
    if COLOR == RED:
        return f"{RED}[{COLOR}-{RED}]{RESET}"
    return f"{GREEN}[{COLOR}+{GREEN}]{RESET}"

def simple_pointer():
    return f"{GREEN} * {RESET} "

#ARGUMENTS PARSER
#Examples
# python ipreco.py <ip>
# python ipreco.py for default ip
#python ipreco.py -d (DNS RESOLUTION)
def args():
    parser = argparse.ArgumentParser(description="IP Geolocation Fetcher")
    parser.add_argument("-d", "--dns", action="store_true", help="Perform DNS resolution")
    parser.add_argument("ip", nargs="?", help="IP address to fetch geolocation data for (default: your own IP)")
    return parser.parse_args()

#Simple IP validation function
def validate_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


#EXAMPLE: GET https://ip.guide/{IP} -> RESPONSE -> JSON 
def get_requests(url, ip=None):
    RED_POINT = pointers(RED)
    try:
        if ip:
            response = requests.get(f"{url}{ip}")
            if response.status_code != 200:
                print(f"{RED_POINT}{RED} Error: Code {response.status_code}.{RESET}")
                return None
            return response.json()
        else:
            #If no IP provided, get own IP data -> GET https://ip.guide/
            response = requests.get(f"{url}")
            if response.status_code != 200:
                print(f"{RED_POINT}{RED} Error: Code {response.status_code}.{RESET}")
                return None
            return response.json()
    except Exception as e:
        print(f"{RED_POINT}{RED} Error: {url} {e}")
        return None

#Desglose data function from response JSON
def desglose_data(data):
    try:
        ip = data["ip"]
        hosts = data["network"]["hosts"]
        location = data["location"]
        system = data["network"]["autonomous_system"]

        #Name -> "name - organization (country) - ASN: asn"
        name = f"{system['name']} - {system['organization']} ({system['country']}) - ASN: {system['asn']}"

        #Example IP Range -> "xxx.xxx.xxx.1 - xxx.xxx.xxx.16"
        range_ip = f"{hosts['start']} - {hosts['end']}"
        city = location['city'] if location['city'] else "Unknown"
        country = location['country']
        timezone = location['timezone']
        latitude = location['latitude']
        longitude = location['longitude']
        #Return all desglose data
        return ip, range_ip, name, city, country, timezone, latitude, longitude
    except TypeError as e:
        RED_POINT = pointers(RED)
        print(f"{RED_POINT}{RED} Data Desglose Error:{RESET}{e}")
        sys.exit(1)

#Simple DNS resolution function
def dns_resolution(IP):
    RED_POINT = pointers(RED)
    try:
        # Socket (IP) -> gethost -> DNS Info -> hostname
        hostname, _, _ = socket.gethostbyaddr(IP)
        return hostname
    except (socket.herror, socket.gaierror) as e:
        print(f"{RED_POINT}{RED} DNS Resolution Error.{RESET}")
        return None

#Print beautiful results function
def print_results(ip, range_ip, name, city, country, timezone, latitude, longitude, hostname=None):
    print(f"{GREEN}\nGeolocation Data Retrieved:{RESET}")
    print(f"\n{ip} -> {name}\n")
    print(f"{simple_pointer()}IP Range: {range_ip}")
    if hostname is not None:
        print(f"{simple_pointer()}Hostname: {hostname}")
    print(f"{simple_pointer()}City: {city}")
    print(f"{simple_pointer()}Country: {country}")
    print(f"{simple_pointer()}Timezone: {timezone}")
    print(f"{simple_pointer()}Latitude: {latitude} - Longitude: {longitude}\n")

#MAIN FUNCTION
def main():
    BLUE_POINT = pointers(BLUE)
    RED_POINT = pointers(RED)

    print(f"{GREEN}{BANNER}{RESET}")
    print(f"{YELLOW}Created by mZam1a\nGitHub: {BLUE}https://github.com/mZam1a{RESET}\n")

    arguments = args()
    target_ip = arguments.ip if arguments.ip else None

    if target_ip and not validate_ip(target_ip):
        print(f"{RED}{RED_POINT} Invalid IP address provided.{RESET}")
        return

    print(f"{BLUE}{BLUE_POINT} Target IP: {target_ip}{RESET}")

    #Get data from get_requests function
    data = get_requests(URL, target_ip)
    
    #If data is None, end program
    if data is None:
        return

    #Validate and desglose data from JSON response
    ip, range_ip, name, city, country, timezone, latitude, longitude = desglose_data(data)
    hostname = dns_resolution(ip) if ip and arguments.dns else None
    print_results(ip, range_ip, name, city, country, timezone, latitude, longitude, hostname)

if __name__ == "__main__":
    main()
