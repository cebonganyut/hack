import socket
import requests
import re
import sys
import threading
from queue import Queue
from colorama import Fore, init
from itertools import cycle
from multiprocessing.dummy import Pool as ThreadPool

init()  # Inisialisasi colorama

white = Fore.LIGHTWHITE_EX
red = Fore.LIGHTRED_EX
green = Fore.LIGHTGREEN_EX
yellow = Fore.LIGHTYELLOW_EX
cyan = Fore.CYAN

def check_port(ip, port):
    try:
        ip = ip.strip()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except:
        return False

def taz(ip):
    ip = ip.strip()
    port_80_open = check_port(ip, 80)
    port_443_open = check_port(ip, 443)

    if port_80_open or port_443_open:
        if port_80_open and port_443_open:
            print(green + f'[>>] Good IP (80 & 443 open) >>> {ip}' + white)
        elif port_80_open:
            print(cyan + f'[>>] Good IP (80 open) >>> {ip}' + white)
        else:
            print(cyan + f'[>>] Good IP (443 open) >>> {ip}' + white)
        open('Result/Goodip_80_443.txt', 'a').write(ip + '\n')
    else:
        print(red + f'[xx] Bad IP >>> {ip}' + white)
        open('Result/Badip.txt', 'a').write(ip + '\n')

banner = '''
Tools by insan1337 with chat gpt
A Private Tool To Check GoodIPS for Port 80 and 443
'''

print(banner)

ip_list_file = input('Enter IP list file: ')
thread_count = input('Enter thread count: ')

with open(ip_list_file, 'r') as f:
    ip_list = f.readlines()

pool = ThreadPool(int(thread_count))
pool.map(taz, ip_list)
pool.close()
pool.join()

if __name__ == '__main__':
    print('Done! Check Result folder for output files:')
    print('- Goodip_80_443.txt (IPs with either 80 or 443 or both open)')
    print('- Badip.txt (IPs with neither 80 nor 443 open)')
