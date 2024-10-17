import requests
from urllib.parse import urljoin
import concurrent.futures
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

def check_file_exists(base_url, file_path):
    if not base_url.endswith('/'):
        base_url += '/'
    full_url = urljoin(base_url, file_path)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(full_url, allow_redirects=True, timeout=10, headers=headers)
        
        if response.status_code == 200:
            content = response.text.lower()

            error_patterns = ['not found', 'error 404', 'file not found', 'page not found']
            if any(pattern in content for pattern in error_patterns):
                return "Not Found", full_url

            if len(content) < 100:
                return "Not Found", full_url

            content_type = response.headers.get('Content-Type', '').lower()
            expected_type = get_expected_content_type(file_path)
            if expected_type and expected_type not in content_type:
                return "Not Found", full_url

            if file_path.endswith('.php'):
                if '<?php' not in content:
                    return "Not Found", full_url

            return "Found", full_url

        else:
            return "Not Found", full_url

    except requests.RequestException:
        return "Not Found", full_url

def get_expected_content_type(file_path):
    extension = file_path.split('.')[-1].lower()
    type_map = {
        'php': 'text/html',
        'html': 'text/html',
        'js': 'application/javascript',
        'css': 'text/css',
        'jpg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif'
    }
    return type_map.get(extension)

def process_single_url(url, paths, num_threads):
    found_files = []
    
    def check_path(path):
        status, full_url = check_file_exists(url, path)
        if status == "Found":
            print(f"{Fore.GREEN}[Found] {full_url}{Style.RESET_ALL}")
            return full_url
        else:
            print(f"{Fore.RED}[Not Found] {full_url}{Style.RESET_ALL}")
        return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_to_path = {executor.submit(check_path, path): path for path in paths}
        for future in concurrent.futures.as_completed(future_to_path):
            result = future.result()
            if result:
                found_files.append(result)
    
    return found_files

def main():
    urls_input = input("Enter path to a file containing URLs: ").strip()
    with open(urls_input, 'r') as file:
        urls = [line.strip() for line in file if line.strip()]

    paths_input = input("Enter path to a file containing file paths to check: ").strip()
    with open(paths_input, 'r') as file:
        paths = [line.strip() for line in file if line.strip()]

    while True:
        try:
            num_threads = int(input("Enter the number of threads to use for each website (1-100): "))
            if 1 <= num_threads <= 100:
                break
            else:
                print("Please enter a number between 1 and 100.")
        except ValueError:
            print("Please enter a valid number.")

    all_found_files = []

    for url in urls:
        print(f"\nProcessing {url}...")
        found_files = process_single_url(url, paths, num_threads)
        all_found_files.extend(found_files)
        print(f"Completed checking {url}. Found {len(found_files)} files.")

    with open('found_files.txt', 'w') as file:
        for full_url in all_found_files:
            file.write(f"{full_url}\n")

    print(f"\nAll found files saved to 'found_files.txt'")
    print(f"Total files found: {len(all_found_files)}")

if __name__ == "__main__":
    main()
