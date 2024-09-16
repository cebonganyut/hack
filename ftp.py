import requests
import os
import json
from colorama import Fore, Style, init
from pyfiglet import Figlet
from concurrent.futures import ThreadPoolExecutor

init(autoreset=True)

# Function to display the banner using pyfiglet
def Banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    
    figlet = Figlet(font='block')
    print(Fore.GREEN + figlet.renderText("FTP & Config"))
    
    figlet = Figlet(font='starwars')
    print(Fore.YELLOW + figlet.renderText("MAINHACK"))
    print("")

# Helper function to write to files, avoiding duplicates
def log_to_file(filename, url):
    with open(filename, "a+", encoding='utf-8') as file:
        file.seek(0)
        existing_urls = set(file.read().splitlines())
        if url not in existing_urls:
            file.write(url + "\n")

# Function to check a URL for configuration files
def check_url(url):
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    
    for path in paths:
        full_url = url + path
        try:
            response = requests.get(full_url, headers=headers, timeout=timeout)
            
            if response.status_code == 200:
                response_text = response.text
                # Check for FTP-related content in the response text
                if any(keyword in response_text for keyword in ["uploadOnSave", "upload_on_save", "save_before_upload"]):
                   
