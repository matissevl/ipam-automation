import time
import pynetbox
import requests
import urllib3

# Disable insecure request warnings for HTTPS without a valid certificate
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
url = "http://192.168.101.10:8000"  # Replace with your NetBox URL
token = "2247a0371d4e186a5c78f3e13417970d5672b3b1"  # Replace with your API token

# Setup pynetbox session
session = requests.Session()
session.verify = False  # Disable SSL verification
nb = pynetbox.api(url, token=token, threading=False)  # Disable threading
nb.http_session = session


# Function to measure query performance
def measure_query(query_func, description):
    start = time.perf_counter()
    result = query_func()
    end = time.perf_counter()
    result_count = len(result) if hasattr(result, "__len__") else 1 if result else 0
    print(f"{description}: {end - start:.4f} seconds | Result Count: {result_count}")


# Function to print total amounts
def print_totals():
    try:
        total_ips = len(nb.ipam.ip_addresses.filter(dummy_param=time.time()))
        total_prefixes = len(nb.ipam.prefixes.filter(dummy_param=time.time()))
        print(f"Total IP Addresses: {total_ips}")
        print(f"Total Prefixes: {total_prefixes}")
    except Exception as e:
        print(f"Error fetching totals: {e}")


# Test cases
def test_queries():
    # Single IP lookup
    measure_query(
        lambda: nb.ipam.ip_addresses.get(address="10.0.0.242/26", _cache=False),
        "Single IP Lookup",
    )
    time.sleep(1)  # Add delay

    # Bulk IPs in a subnet
    measure_query(
        lambda: nb.ipam.ip_addresses.filter(parent="10.0.0.0/28", _cache=False),
        "Bulk IP Query (Subnet /16)",
    )
    time.sleep(1)  # Add delay

    # Fetch all prefixes
    measure_query(
        lambda: nb.ipam.prefixes.filter(dummy_param=time.time()), "Fetch All Prefixes"
    )
    time.sleep(1)  # Add delay

    # Search for specific prefix
    measure_query(
        lambda: nb.ipam.prefixes.filter(prefix="10.0.1.0/24", _cache=False),
        "Single Prefix Lookup",
    )
    time.sleep(1)  # Add delay


# Run the tests
if __name__ == "__main__":
    print_totals()
    test_queries()
