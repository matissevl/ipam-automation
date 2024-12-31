import json
import pynetbox
import requests
import urllib3
import logging
from logging.handlers import RotatingFileHandler
import argparse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Set up argument parser
parser = argparse.ArgumentParser(description="Insert or update IP addresses.")
parser.add_argument("url", help="The URL of the NetBox instance")
parser.add_argument("token", help="The API token for authentication")
parser.add_argument("json_file", help="The JSON file containing IP addresses")
parser.add_argument("--log_file", help="The log file")

args = parser.parse_args()

# Configure logging
if args.log_file:
    handler = RotatingFileHandler(args.log_file, maxBytes=10485760, backupCount=5)
    logging.basicConfig(
        handlers=[handler],
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
else:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

url = args.url
token = args.token
json_file_path = args.json_file

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure the session with retries
session = requests.Session()
retry_strategy = Retry(
    total=3,  # Number of retries
    backoff_factor=1,  # Wait time between retries (1, 2, 4 seconds)
    status_forcelist=[500, 502, 503, 504],  # Retry on specific HTTP errors
    allowed_methods=[
        "HEAD",
        "GET",
        "POST",
        "PUT",
        "DELETE",
    ],  # Retry only on safe methods
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

# Initialize pynetbox API
nb = pynetbox.api(
    url,
    token=token,
    threading=True,
)

nb.http_session = session

try:
    # Load the JSON file
    with open(json_file_path) as f:
        input_ips = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    logging.error(f"Error loading JSON file: {e}")
    exit(1)

try:
    # Retrieve current IP addresses from NetBox
    current_ips = list(nb.ipam.ip_addresses.all())
except pynetbox.RequestError as e:
    logging.error(f"Error retrieving current IP addresses: {e}")
    exit(1)

# Convert current IP addresses to a dictionary for easy lookup
current_ips_dict = {ip.address: ip for ip in current_ips}

# Process input IP addresses
for input_ip in input_ips:
    ip_address = input_ip["address"]
    if ip_address in current_ips_dict:
        # IP address exists, check for updates
        ip = current_ips_dict[ip_address]
        updated = False
        if ip.status.value != input_ip["status"]:
            ip.status = input_ip["status"]
            updated = True
        if ip.dns_name != input_ip["dns_name"]:
            ip.dns_name = input_ip["dns_name"]
            updated = True
        if ip.description != input_ip["description"]:
            ip.description = input_ip["description"]
            updated = True
        if ip.vrf.name != input_ip["vrf"]:
            vrf_name = input_ip["vrf"]
            try:
                vrf = nb.ipam.vrfs.get(name=vrf_name)
                if vrf:
                    ip.vrf = vrf.id
                    updated = True
                else:
                    logging.error(f"VRF with name {vrf_name} not found")
            except pynetbox.RequestError as e:
                logging.error(f"Error retrieving VRF with name={vrf_name}: {e}")
        if updated:
            try:
                logging.info(f"Updating IP address {ip_address}")
                ip.save()
            except pynetbox.RequestError as e:
                logging.error(f"Error updating IP address {ip_address}: {e}")
    else:
        # IP address does not exist, create it
        try:
            logging.info(f"Creating IP address {ip_address}")
            if "vrf" in input_ip:
                vrf_name = input_ip["vrf"]
                vrf = nb.ipam.vrfs.get(name=vrf_name)
                if vrf:
                    input_ip["vrf"] = vrf.id
                else:
                    logging.error(f"VRF with name {vrf_name} not found")
                    continue
            nb.ipam.ip_addresses.create(input_ip)
        except pynetbox.RequestError as e:
            logging.error(f"Error creating IP address {ip_address}: {e}")

# Delete IP addresses that are not in the input JSON
input_ip_addresses = {ip["address"] for ip in input_ips}
for ip in current_ips:
    if ip.address not in input_ip_addresses:
        try:
            logging.info(f"Deleting IP address {ip.address}")
            ip.delete()
        except pynetbox.RequestError as e:
            logging.error(f"Error deleting IP address {ip.address}: {e}")
