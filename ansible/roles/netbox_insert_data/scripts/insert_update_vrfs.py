import json
import pynetbox
import requests
import urllib3
import logging
from logging.handlers import RotatingFileHandler
import argparse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# http://192.168.101.10:8000 2247a0371d4e186a5c78f3e13417970d5672b3b1

# Set up argument parser
parser = argparse.ArgumentParser(description="Insert or update VRFs.")
parser.add_argument("url", help="The URL of the NetBox instance")
parser.add_argument("token", help="The API token for authentication")
parser.add_argument("json_file", help="The JSON file containing VRFs")
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
        input_vrfs = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    logging.error(f"Error loading JSON file: {e}")
    exit(1)

try:
    # Retrieve current VRFs from NetBox
    current_vrfs = list(nb.ipam.vrfs.all())
except pynetbox.RequestError as e:
    logging.error(f"Error retrieving current VRFs: {e}")
    exit(1)

# Convert current VRFs to a dictionary for easy lookup
current_vrfs_dict = {vrf.name: vrf for vrf in current_vrfs}

# Process input VRFs
for input_vrf in input_vrfs:
    vrf_name = input_vrf["name"]
    if vrf_name in current_vrfs_dict:
        # VRF exists, check for updates
        vrf = current_vrfs_dict[vrf_name]
        updated = False
        if vrf.rd != input_vrf["rd"]:
            vrf.rd = input_vrf["rd"]
            updated = True
        if vrf.description != input_vrf["description"]:
            vrf.description = input_vrf["description"]
            updated = True
        if updated:
            try:
                logging.info(f"Updating VRF {vrf_name}")
                vrf.save()
            except pynetbox.RequestError as e:
                logging.error(f"Error updating VRF {vrf_name}: {e}")
    else:
        # VRF does not exist, create it
        try:
            logging.info(f"Creating VRF {vrf_name}")
            nb.ipam.vrfs.create(input_vrf)
        except pynetbox.RequestError as e:
            logging.error(f"Error creating VRF {vrf_name}: {e}")

# # Delete VRFs that are not in the input JSON
# input_vrf_names = {vrf["name"] for vrf in input_vrfs}
# for vrf in current_vrfs:
#     if vrf.name not in input_vrf_names:
#         try:
#             logging.info(f"Deleting VRF {vrf.name}")
#             vrf.delete()
#         except pynetbox.RequestError as e:
#             logging.error(f"Error deleting VRF {vrf.name}: {e}")
