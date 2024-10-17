import requests
from urllib.parse import urljoin
import concurrent.futures
import re
import hashlib

def get_file_signature(content):
    return hashlib.md5(content[:1024]).hexdigest()

def check_file_exists(base_url, file_path):
    if not base_url.endswith('/'):
        base_url += '/'
    full_url = urljoin(base_url, file_path)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # Step 1: Try GET request (skip HEAD for more accuracy)
        response = requests.get(full_url, allow_redirects=True, timeout=10, headers=headers)
        
        # Check status code
        if response.status_code == 200:
            content = response.content
            text = response.text.lower()

            # Step 2: Analyze content for common error patterns
            error_patterns = ['not found', 'error 404', 'file not found', 'page not found']
            if any(pattern in text for pattern in error_patterns):
                return "Not Found (Error Page)", None

            # Step 3: Check content length and type
            if len(content) < 100:  # Arbitrary small size, adjust as needed
                return "Suspicious (Small Content)", None

            # Step 4: Check content type
            content_type = response.headers.get('Content-Type', '').lower()
            expected_type = get_expected_content_type(file_path)
            if expected_type and expected_type not in content_type:
                return f"Suspicious (Unexpected Content-Type: {content_type})", None

            # Step 5: Additional checks for specific file types
            if file_path.endswith('.php'):
                if '<?php' not in text:
                    return "Suspicious (No PHP code found)", None

            # If all checks pass, consider the file found
            return "Found", full_url, get_file_signature(content)

        elif response.status_code == 403:
            return "Access Forbidden", None
        elif response.status_code == 404:
            return "Not Found", None
        else:
            return f"Not Found (Status {response.status_code})", None

    except requests.RequestException as e:
        return f"Error: {str(e)}", None

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
        result = check_file_exists(url, path)
        if result[0] == "Found":
            return result
        return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_to_path = {executor.submit(check_path, path): path for path in paths}
        for future in concurrent.futures.as_completed(future_to_path):
            result = future.result()
            if result:
                found_files.append(result)
    
    return found_files

def main():
    # Input for URLs
    urls_input = input("Enter path to a file containing URLs: ").strip()
    with open(urls_input, 'r') as file:
        urls = [line.strip() for line in file if line.strip()]

    # Input for paths
    paths_input = input("Enter path to a file containing file paths to check: ").strip()
    with open(paths_input, 'r') as file:
        paths = [line.strip() for line in file if line.strip()]

    # Input for number of threads
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

    # Process URLs sequentially
    for url in urls:
        print(f"\nProcessing {url}...")
        found_files = process_single_url(url, paths, num_threads)
        all_found_files.extend(found_files)
        print(f"Completed checking {url}. Found {len(found_files)} files.")

    # Save found files to txt with additional information
    with open('found_files.txt', 'w') as file:
        for status, full_url, signature in all_found_files:
            file.write(f"{full_url} | {signature}\n")

    print(f"\nAll found files saved to 'found_files.txt'")
    print(f"Total files found: {len(all_found_files)}")

if __name__ == "__main__":
    main()
