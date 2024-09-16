import requests
import os
import json
from colorama import Fore, Style, init
from cfonts import say
from concurrent.futures import ThreadPoolExecutor

init(autoreset=True)

# Function to display the banner using cfonts
def Banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    say("FTP & Config", colors=["green", "blue"], align="center", font="block")
    say("MAINHACK", space=False, font="console", colors=["white"], background="blue", align="center")
    print("")

# Helper function to write to files
def log_to_file(filename, url):
    with open(filename, "a+") as file:
        file.seek(0)
        if url not in file.read():
            file.write(url + "\n")

# Function to check a URL for configuration files
def check_url(url):
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url
    
    for path in paths:
        full_url = url + path
        try:
            response = requests.get(full_url, headers=headers, timeout=timeout)
            
            if response.status_code == 200:
                response_text = response.text
                # Check for FTP-related content in the response text
                if "uploadOnSave" in response_text or "upload_on_save" in response_text or "save_before_upload" in response_text:
                    print(Fore.GREEN + f"Found FTP: {full_url}" + Style.RESET_ALL)
                    log_to_file("validftp.txt", full_url)
                # Check for database configuration content in the response
                if "DB_HOST" in response_text or "db_host" in response_text:
                    print(Fore.GREEN + f"Found Config: {full_url}" + Style.RESET_ALL)
                    log_to_file("validconfig.txt", full_url)

                # Try to parse JSON to find FTP or DB configurations
                try:
                    json_data = json.loads(response_text)
                    if "ftp" in json_data and "host" in json_data["ftp"]:
                        print(Fore.GREEN + f"Found FTP in JSON: {full_url}" + Style.RESET_ALL)
                        log_to_file("validftp1.txt", full_url)
                    if "db" in json_data and "host" in json_data["db"]:
                        print(Fore.GREEN + f"Found DB Config in JSON: {full_url}" + Style.RESET_ALL)
                        log_to_file("validconfig.txt", full_url)
                except json.JSONDecodeError:
                    pass
            else:
                print(Fore.RED + f"Invalid Response: {full_url}" + Style.RESET_ALL)
        
        except requests.exceptions.RequestException as e:
            print(Fore.RED + f"Error accessing {full_url}: {e}" + Style.RESET_ALL)

# Call the banner function
Banner()

# Get input from the user
input_list = input(f"{Fore.LIGHTRED_EX}[{Fore.LIGHTGREEN_EX}?{Fore.LIGHTRED_EX}] {Fore.WHITE}Give List: ")
with open(input_list, "r") as file:
    urls = file.read().splitlines()

# HTTP headers and timeout settings
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0'}
timeout = 10

# Paths to check for on each URL
paths = [
    "/.vscode/sftp.json",
    "/ftp.json",
    "/sftp-config.json",
    "/config.json",
    "/wp-config.php.bak",
    "/wp-config.php.old",
    "/.env.bak",
    "/.env"
]

# Use ThreadPoolExecutor for concurrent execution
with ThreadPoolExecutor(max_workers=50) as executor:
    executor.map(check_url, urls)
