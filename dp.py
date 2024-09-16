import socket
import threading
from queue import Queue
import os

def resolve_domain(domain, results, lock):
    """
    Resolve a domain to its IP address and store the result.
    """
    try:
        ip_address = socket.gethostbyname(domain)
        with lock:
            if ip_address:
                results.add(ip_address)
            print(f"{domain} resolved to {ip_address}")
    except socket.gaierror as e:
        with lock:
            print(f"Failed to resolve {domain}: {e}")

def worker(domain_queue, results, lock):
    """
    Worker function for resolving domains from the queue.
    """
    while True:
        domain = domain_queue.get()
        if domain is None:
            break
        resolve_domain(domain, results, lock)
        domain_queue.task_done()

def main():
    domain_file = input("Enter the name of the file containing domains: ")
    num_threads = int(input("Enter the number of threads to use: "))
    
    # Ensure the file exists
    if not os.path.isfile(domain_file):
        print(f"File {domain_file} does not exist.")
        return

    # Read domains from file
    with open(domain_file, 'r') as f:
        domains = [line.strip() for line in f if line.strip()]

    if not domains:
        print("No domains found in the file.")
        return

    # Prepare to collect results
    results = set()  # Use a set to automatically handle duplicates
    domain_queue = Queue()
    lock = threading.Lock()

    # Start worker threads
    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=worker, args=(domain_queue, results, lock))
        t.start()
        threads.append(t)

    # Add domains to the queue
    for domain in domains:
        domain_queue.put(domain)

    # Add None to the queue to signal threads to exit
    for _ in range(num_threads):
        domain_queue.put(None)

    # Wait for all threads to complete
    for t in threads:
        t.join()

    # Save results to file
    with open('IPR.txt', 'w', encoding='utf-8') as f:
        for ip in sorted(results):
            f.write(f"{ip}\n")

    print(f"\nResolution completed.")
    print(f"Total domains processed: {len(domains)}")
    print(f"Unique IP addresses saved to IPR.txt")

if __name__ == "__main__":
    main()
