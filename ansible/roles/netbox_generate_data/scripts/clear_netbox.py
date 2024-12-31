import requests
import argparse

# Set up argument parser
parser = argparse.ArgumentParser(
    description="Clear NetBox by deleting all VRFs, subnets, VLANs, and IP addresses."
)
parser.add_argument("netbox_url", help="The base URL of the NetBox instance")
parser.add_argument("token", help="The API token for authentication")

args = parser.parse_args()

headers = {
    "Authorization": f"Token {args.token}",
    "Content-Type": "application/json",
}


def delete_all(endpoint):
    url = f"{args.netbox_url}/api/{endpoint}/"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    items = response.json()["results"]
    for item in items:
        delete_url = f"{url}{item['id']}/"
        delete_response = requests.delete(delete_url, headers=headers)
        delete_response.raise_for_status()
        print(f"Deleted {endpoint[:-1]} with ID {item['id']}")


# Delete all VRFs
delete_all("ipam/vrfs")

# Delete all subnets
delete_all("ipam/prefixes")

# Delete all VLANs
delete_all("ipam/vlans")

# Delete all IP addresses
delete_all("ipam/ip-addresses")
