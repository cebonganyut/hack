import os
import concurrent.futures
import time
import threading
import random
import string
import json
import ctypes
import sys

try:
    import requests
    import colorama
    import pystyle
    import datetime
    import aiosocks
    import asyncio
    import aiohttp_socks
    import socks
    import socket
    import tls_client
except ModuleNotFoundError:
    os.system("pip install requests colorama pystyle datetime aiosocks asyncio aiohttp-socks socks tls_client")

from pystyle import Write, System, Colors, Colorate, Anime
from colorama import Fore, Style
from datetime import datetime
from aiohttp_socks import ProxyConnector, ProxyType

https_scraped = 0
socks4_scraped = 0
socks5_scraped = 0

http_checked = 0
socks4_checked = 0
socks5_checked = 0

red = Fore.RED
yellow = Fore.YELLOW
green = Fore.GREEN
blue = Fore.BLUE
orange = Fore.RED + Fore.YELLOW
pretty = Fore.LIGHTMAGENTA_EX + Fore.LIGHTCYAN_EX
magenta = Fore.MAGENTA
lightblue = Fore.LIGHTBLUE_EX
cyan = Fore.CYAN
gray = Fore.LIGHTBLACK_EX + Fore.WHITE
reset = Fore.RESET
pink = Fore.LIGHTGREEN_EX + Fore.LIGHTMAGENTA_EX
dark_green = Fore.GREEN + Style.BRIGHT
output_lock = threading.Lock()

def get_time_rn():
    date = datetime.now()
    hour = date.hour
    minute = date.minute
    second = date.second
    timee = "{:02d}:{:02d}:{:02d}".format(hour, minute, second)
    return timee

def update_title():
    global https_scraped, socks4_scraped, socks5_scraped
    ctypes.windll.kernel32.SetConsoleTitleW(f'insan1337 ❤️')

def update_title2():
    global http_checked, socks4_checked, socks5_checked
    ctypes.windll.kernel32.SetConsoleTitleW(f'insan1337 ❤️')

def ui():
    ctypes.windll.kernel32.SetConsoleTitleW(f"insan1337 ❤️")
    System.Clear()
    Write.Print(f"""
insan1337                                                                                  
                                                                                  
\t\t[ This tool is a scraper & checker for HTTP/s, SOCKS4, and SOCKS5 proxies. ]
\t\t\t\t\t[ The Best Ever Not Gonna Lie ]                                                                          
""", Colors.red_to_blue, interval=0.000)
    time.sleep(3)

ui()

def load_urls_from_file(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]

# Input untuk file list URL
api_file = input("Masukkan nama file untuk semua jenis proxy links (atau tekan Enter untuk menggunakan default): ")

if api_file:
    # Jika file diinputkan, gunakan semua URL dari file untuk semua jenis proxy
    all_urls = load_urls_from_file(api_file)
    http_links = socks4_list = socks5_list = all_urls
else:
    # Jika tidak ada input file, gunakan list default
    http_links = [
        "https://api.proxyscrape.com/?request=getproxies&proxytype=https&timeout=10000&country=all&ssl=all&anonymity=all",
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        # ... (tambahkan URL lainnya sesuai kebutuhan)
    ]

    socks4_list = [
        "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks4",
        "https://api.proxyscrape.com/?request=displayproxies&proxytype=socks4&country=all",
        "https://api.openproxylist.xyz/socks4.txt",
        # ... (tambahkan URL lainnya sesuai kebutuhan)
    ]

    socks5_list = [
        "https://raw.githubusercontent.com/B4RC0DE-TM/proxy-list/main/SOCKS5.txt",
        "https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies/socks5.txt",
        "https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks5.txt",
        # ... (tambahkan URL lainnya sesuai kebutuhan)
    ]

# Input untuk jumlah thread
while True:
    try:
        num_threads = int(input("Masukkan jumlah thread yang diinginkan: "))
        if num_threads > 0:
            break
        else:
            print("Jumlah thread harus lebih dari 0.")
    except ValueError:
        print("Masukkan angka yang valid.")

def scrape_proxy_links(link, proxy_type):
    global https_scraped, socks4_scraped, socks5_scraped
    response = requests.get(link)
    if response.status_code == 200:
        with output_lock:
            time_rn = get_time_rn()
            print(f"[ {pink}{time_rn}{reset} ] | ( {green}SUCCESS{reset} ) {pretty}Scraped --> ", end='')
            sys.stdout.flush()
            Write.Print(link[:60] + "*******\n", Colors.purple_to_red, interval=0.000)
        proxies = response.text.splitlines()
        if proxy_type == "http":
            https_scraped += len(proxies)
        elif proxy_type == "socks4":
            socks4_scraped += len(proxies)
        elif proxy_type == "socks5":
            socks5_scraped += len(proxies)
        update_title()
        return proxies
    return []

def scrape_and_save(links, proxy_type, filename):
    proxies = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        results = executor.map(lambda link: scrape_proxy_links(link, proxy_type), links)
        for result in results:
            proxies.extend(result)

    with open(filename, "w") as file:
        for proxy in proxies:
            if ":" in proxy and not any(c.isalpha() for c in proxy):
                file.write(proxy + '\n')

scrape_and_save(http_links, "http", "http_proxies.txt")
scrape_and_save(socks4_list, "socks4", "socks4_proxies.txt")
scrape_and_save(socks5_list, "socks5", "socks5_proxies.txt")

time.sleep(1)
nameFile = f"Results"
if not os.path.exists(nameFile):
    os.mkdir(nameFile)

for file_type in ["http", "socks4", "socks5"]:
    with open(f"Results/{file_type}.txt", "w") as f:
        f.write("")

valid_http = []
valid_socks4 = []
valid_socks5 = []

def check_proxy_http(proxy):
    global http_checked
    proxy_dict = {
        "http": "http://" + proxy,
        "https": "https://" + proxy
    }
    try:
        url = 'http://httpbin.org/get' 
        r = requests.get(url, proxies=proxy_dict, timeout=30)
        if r.status_code == 200:
            with output_lock:
                time_rn = get_time_rn()
                print(f"[ {pink}{time_rn}{reset} ] | ( {green}VALID{reset} ) {pretty}HTTP/S --> ", end='')
                sys.stdout.flush()
                Write.Print(proxy + "\n", Colors.cyan_to_blue, interval=0.000)
            valid_http.append(proxy)
            http_checked += 1
            update_title2()
            with open(f"Results/http.txt", "a+") as f:
                f.write(proxy + "\n")
    except requests.exceptions.RequestException as e:
        pass

def checker_proxy_socks4(proxy):
    global socks4_checked
    try:
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS4, proxy.split(':')[0], int(proxy.split(':')[1]))
        socket.socket = socks.socksocket
        socket.create_connection(("www.google.com", 443), timeout=5)
        socks4_checked += 1
        update_title2()
        with output_lock:
            time_rn = get_time_rn()
            print(f"[ {pink}{time_rn}{reset} ] | ( {green}VALID{reset} ) {pretty}SOCKS4 --> ", end='')
            sys.stdout.flush()
            Write.Print(proxy + "\n", Colors.cyan_to_blue, interval=0.000)
        with open("Results/socks4.txt", "a+") as f:
            f.write(proxy + "\n")
    except (socks.ProxyConnectionError, socket.timeout, OSError):
        pass

def checker_proxy_socks5(proxy):
    global socks5_checked
    try:
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, proxy.split(':')[0], int(proxy.split(':')[1]))
        socket.socket = socks.socksocket
        socket.create_connection(("www.google.com", 443), timeout=5)
        socks5_checked += 1
        update_title2()
        with output_lock:
            time_rn = get_time_rn()
            print(f"[ {pink}{time_rn}{reset} ] | ( {green}VALID{reset} ) {pretty}SOCKS5 --> ", end='')
            sys.stdout.flush()
            Write.Print(proxy + "\n", Colors.cyan_to_blue, interval=0.000)
        with open("Results/socks5.txt", "a+") as f:
            f.write(proxy + "\n")
    except (socks.ProxyConnectionError, socket.timeout, OSError):
        pass

def check_all(proxy_type, pathTXT):
    with open(pathTXT, "r") as f:
        proxies = f.read().splitlines()

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        if proxy_type == "http":
            executor.map(check_proxy_http, proxies)
        elif proxy_type == "socks4":
            executor.map(checker_proxy_socks4, proxies)
        elif proxy_type == "socks5":
            executor.map(checker_proxy_socks5, proxies)

def LetsCheckIt(proxy_types):
    threadsCrack = []
    for proxy_type in proxy_types:
        if os.path.exists(f"{proxy_type}_proxies.txt"):
            t = threading.Thread(target=check_all, args=(proxy_type, f"{proxy_type}_proxies.txt"))
            t.start()
            threadsCrack.append(t)
    for t in threadsCrack:
        t.join()

proxy_types = ["http", "socks4", "socks5"]
LetsCheckIt(proxy_types)

for file in ["http_proxies.txt", "socks4_proxies.txt", "socks5_proxies.txt"]:
    if os.path.exists(file):
        os.remove(file)

input("Tekan Enter untuk keluar...")
