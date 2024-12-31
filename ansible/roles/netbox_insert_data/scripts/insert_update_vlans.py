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
parser = argparse.ArgumentParser(description="Insert or update VLANs.")
parser.add_argument("url", help="The URL of the NetBox instance")
parser.add_argument("token", help="The API token for authentication")
parser.add_argument("json_file", help="The JSON file containing VLANs")
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

with requests.Session() as session:
    session.verify = False
    nb = pynetbox.api(
        url,
        token=token,
        threading=True,
    )
    nb.http_session = session

    try:
        # Load the JSON file
        with open(json_file_path) as f:
            input_vlans = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading JSON file: {e}")
        exit(1)

    try:
        # Retrieve current VLANs from NetBox
        current_vlans = list(nb.ipam.vlans.all())
    except pynetbox.RequestError as e:
        logging.error(f"Error retrieving current VLANs: {e}")
        exit(1)

    # Convert current VLANs to a dictionary for easy lookup
    current_vlans_dict = {vlan.vid: vlan for vlan in current_vlans}

    # Process input VLANs
    for input_vlan in input_vlans:
        vlan_vid = input_vlan["vid"]
        if vlan_vid in current_vlans_dict:
            # VLAN exists, check for updates
            vlan = current_vlans_dict[vlan_vid]
            updated = False
            if vlan.status.value != input_vlan["status"]:
                vlan.status = input_vlan["status"]
                updated = True
            if vlan.name != input_vlan["name"]:
                vlan.name = input_vlan["name"]
                updated = True
            if updated:
                try:
                    logging.info(f"Updating VLAN {vlan_vid}")
                    vlan.save()
                except pynetbox.RequestError as e:
                    logging.error(f"Error updating VLAN {vlan_vid}: {e}")
        else:
            # VLAN does not exist, create it
            try:
                logging.info(f"Creating VLAN {vlan_vid}")
                nb.ipam.vlans.create(input_vlan)
            except pynetbox.RequestError as e:
                logging.error(f"Error creating VLAN {vlan_vid}: {e}")
