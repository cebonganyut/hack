import requests
import re
import time
import threading
from queue import Queue
import tldextract

def scrape_rapiddns(ip, page):
    url = f"https://rapiddns.io/sameip/{ip}?type=all&format=json&page={page}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        grab = response.text
        
        if '<th scope="row ">' in grab:
            res = re.findall('<td>(?!\-)(?:[a-zA-Z\d\-]{0,62}[a-zA-Z\d]\.){1,126}(?!\d+)[a-zA-Z]{1,63}</td>', grab)
            
            domains = []
            for domain in res:
                domainku = domain.replace('<td>', '').replace('</td>', '')
                prefixes_to_remove = ['ftp.', 'images.', 'cpanel.', 'cpcalendars.', 'cpcontacts.', 
                                      'webmail.', 'webdisk.', 'hostmaster.', 'mail.', 'ns1.', 
                                      'ns2.', 'autodiscover.']
                for prefix in prefixes_to_remove:
                    if domainku.startswith(prefix):
                        domainku = domainku[len(prefix):]
                domains.append(domainku)
            
            return domains
        else:
            return []
    
    except requests.RequestException as e:
        print(f"Error fetching {ip} page {page}: {e}")
        return []

def filter_and_deduplicate(domains):
    """
    Filter out subdomains and remove duplicates. Only keep the main domains.
    """
    # Use tldextract to filter out subdomains and remove duplicates
    unique_domains = set()
    for domain in domains:
        extracted = tldextract.extract(domain)
        main_domain = f"{extracted.domain}.{extracted.suffix}"
        unique_domains.add(main_domain)
    
    return unique_domains

def worker(ip_queue, all_domains, lock, start_page, end_page):
    while True:
        ip = ip_queue.get()
        if ip is None:
            break

        ip_domains = set()
        for page in range(start_page, end_page + 1):
            page_domains = scrape_rapiddns(ip, page)
            if not page_domains:
                # Stop if no more data is available
                break
            ip_domains.update(page_domains)
            time.sleep(1)  # Be nice to the server

        # Filter and deduplicate domains
        ip_domains = filter_and_deduplicate(ip_domains)

        with lock:
            all_domains.update(ip_domains)
            print(f"Finished scraping {ip}. Found {len(ip_domains)} unique domains.")

        ip_queue.task_done()

def main():
    ip_file = input("Enter the name of the file containing IP addresses: ")
    num_threads = int(input("Enter the number of threads to use: "))
    start_page = int(input("Enter the starting page number: "))
    end_page = int(input("Enter the ending page number: "))

    with open(ip_file, 'r') as f:
        ip_list = [line.strip() for line in f if line.strip()]

    all_domains = set()
    ip_queue = Queue()
    lock = threading.Lock()

    # Start worker threads
    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=worker, args=(ip_queue, all_domains, lock, start_page, end_page))
        t.start()
        threads.append(t)

    # Add IPs to the queue
    for ip in ip_list:
        ip_queue.put(ip)

    # Add None to the queue to signal threads to exit
    for _ in range(num_threads):
        ip_queue.put(None)

    # Wait for all threads to complete
    for t in threads:
        t.join()

    # Save domains to file
    with open('Domains.txt', 'w', encoding='utf-8') as f:
        for domain in sorted(all_domains):
            f.write(domain + '\n')

    print(f"\nScraping completed.")
    print(f"Total IPs processed: {len(ip_list)}")
    print(f"Total unique domains found: {len(all_domains)}")
    print("Results saved to Domains.txt")

if __name__ == "__main__":
    main()
