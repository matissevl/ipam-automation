import json
import pynetbox
import requests
import urllib3
import logging
from logging.handlers import RotatingFileHandler
import argparse
import time
from requests.exceptions import ConnectionError
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Set up argument parser
parser = argparse.ArgumentParser(description="Insert or update subnets.")
parser.add_argument("url", help="The URL of the NetBox instance")
parser.add_argument("token", help="The API token for authentication")
parser.add_argument("json_file", help="The JSON file containing subnets")
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
        input_subnets = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    logging.error(f"Error loading JSON file: {e}")
    exit(1)

try:
    # Retrieve current subnets from NetBox
    current_subnets = list(nb.ipam.prefixes.all())
except pynetbox.RequestError as e:
    logging.error(f"Error retrieving current subnets: {e}")
    exit(1)

# Convert current subnets to a dictionary for easy lookup
current_subnets_dict = {subnet.prefix: subnet for subnet in current_subnets}


def create_prefix_with_retries(nb, input_subnet, max_retries=5, backoff_factor=0.3):
    for attempt in range(max_retries):
        try:
            nb.ipam.prefixes.create(input_subnet)
            return
        except (ConnectionError, requests.exceptions.RequestException) as e:
            if attempt < max_retries - 1:
                sleep_time = backoff_factor * (2**attempt)
                print(f"Connection error: {e}. Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                print(f"Failed to create prefix after {max_retries} attempts.")
                raise


# Process input subnets
for input_subnet in input_subnets:
    subnet_prefix = input_subnet["prefix"]
    if subnet_prefix in current_subnets_dict:
        # Subnet exists, check for updates
        subnet = current_subnets_dict[subnet_prefix]
        updated = False
        if subnet.status.value != input_subnet["status"]:
            subnet.status = input_subnet["status"]
            updated = True
        if subnet.description != input_subnet["description"]:
            subnet.description = input_subnet["description"]
            updated = True
        if subnet.comments != input_subnet["comments"]:
            subnet.comments = input_subnet["comments"]
            updated = True
        if subnet.vlan and subnet.vlan != input_subnet["vlan"]:
            vlan_id = input_subnet["vlan"]
            try:
                vlan = nb.ipam.vlans.get(vid=vlan_id)
                if vlan:
                    subnet.vlan = vlan.id
                    updated = True
                else:
                    logging.error(f"VLAN with ID {vlan_id} not found")
            except pynetbox.RequestError as e:
                logging.error(f"Error retrieving VLAN with ID={vlan_id}: {e}")
        if subnet.vrf:
            vrf = nb.ipam.vrfs.get(subnet.vrf)
            if vrf and vrf.name != input_subnet["vrf"]:
                vrf_name = input_subnet["vrf"]
                try:
                    new_vrf = nb.ipam.vrfs.get(name=vrf_name)
                    if new_vrf:
                        subnet.vrf = new_vrf.id
                        updated = True
                    else:
                        logging.error(f"VRF with name {vrf_name} not found")
                except pynetbox.RequestError as e:
                    logging.error(f"Error retrieving VRF with name={vrf_name}: {e}")
        if updated:
            try:
                logging.info(f"Updating subnet {subnet_prefix}")
                subnet.save()
            except pynetbox.RequestError as e:
                if "Duplicate prefix found" in str(e):
                    logging.warning(
                        f"Skipping update for subnet {subnet_prefix} due to duplicate prefix error"
                    )
                else:
                    logging.error(f"Error updating subnet {subnet_prefix}: {e}")
    else:
        # Subnet does not exist, create it
        try:
            logging.info(f"Creating subnet {subnet_prefix}")
            if "vrf" in input_subnet:
                vrf_name = input_subnet["vrf"]
                vrf = nb.ipam.vrfs.get(name=vrf_name)
                if vrf:
                    input_subnet["vrf"] = vrf.id
                else:
                    logging.error(f"VRF with name {vrf_name} not found")
                    continue
            if "vlan" in input_subnet:
                vlan_id = input_subnet["vlan"]
                vlan = nb.ipam.vlans.get(vid=vlan_id)
                if vlan:
                    input_subnet["vlan"] = vlan.id
                else:
                    logging.error(f"VLAN with ID {vlan_id} not found")
                    continue
            create_prefix_with_retries(nb, input_subnet)
        except pynetbox.RequestError as e:
            logging.error(f"Error creating subnet {subnet_prefix}: {e}")

# Delete subnets that are not in the input JSON
input_subnet_prefixes = {subnet["prefix"] for subnet in input_subnets}
for subnet in current_subnets:
    if subnet.prefix not in input_subnet_prefixes:
        try:
            logging.info(f"Deleting subnet {subnet.prefix}")
            subnet.delete()
        except pynetbox.RequestError as e:
            logging.error(f"Error deleting subnet {subnet.prefix}: {e}")
