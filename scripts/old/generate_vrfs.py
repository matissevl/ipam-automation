import json
import argparse

# import requests
import random
import pynipap
from pynipap import VRF, AuthOptions

pynipap.xmlrpc_uri = "http://webadmin:NHTvu1aNFb61Lzy75HxN@192.168.101.20:1337/XMLRPC"

a = AuthOptions({"authoritative_source": "python-nipap"})


def generate_unique_vrfs(count):
    vrfs = []
    for i in range(count):
        name = f"Test VRF {i+1}"
        rt = f"65000:{100 + i}"
        vrfs.append(
            {
                "name": name,
                "rt": rt,
                "description": f"This is test VRF {i+1}",
            }
        )
    return vrfs


def save_vrfs_to_json(vrfs, filename):
    with open(filename, "w") as f:
        json.dump(vrfs, f, indent=4)


def get_vrf_id(vrf_name):
    search_result = VRF.smart_search(vrf_name, a)
    if search_result["result"]:
        return search_result["result"][0].id
    return None


def generate_unique_prefixes(count):
    prefixes = []
    countries = ["US", "CA", "GB", "DE", "FR"]
    statuses = ["assigned", "reserved", "quarantine"]
    types = ["reservation", "assignment"]  # "host"

    for i in range(count):
        prefix_type = random.choice(types)
        if prefix_type == "host":
            prefix = f"192.168.{i}.255/32"
        else:
            prefix = f"192.168.{i}.0/24"
        vrf_name = f"Test VRF {i+1}"
        vrf_id = get_vrf_id(vrf_name)
        prefix_data = {
            "prefix": prefix,
            "prefix_length": 32 if prefix_type == "host" else 24,
            "display_prefix": prefix,
            "vrf_id": vrf_id,
            "vrf_rt": f"65000:{100 + i}",
            "vrf_name": vrf_name,
            "description": f"This is test prefix {i+1}",
            "comment": "",
            "pool_id": None,
            "pool_name": None,
            "type": prefix_type,
            "status": random.choice(statuses),
            "country": random.choice(countries),
            "order_id": random.randint(1000, 9999),
            "customer_id": random.randint(1000, 9999),
            "vlan": 0,
            "tags": [],
            "avps": {},
            "expires": "never",
            "external_key": None,
            "authoritative_source": "script",
            "alarm_priority": "critical",
            "monitor": True,
        }
        if prefix_type != "reservation" and prefix_type != "assignment":
            prefix_data["node"] = ""
        prefixes.append(prefix_data)
    return prefixes


def save_prefixes_to_json(prefixes, filename):
    with open(filename, "w") as f:
        json.dump(prefixes, f, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate unique VRFs and prefixes and save to JSON files."
    )
    parser.add_argument("vrf_filename", type=str, help="Output JSON file name for VRFs")
    parser.add_argument(
        "prefix_filename", type=str, help="Output JSON file name for prefixes"
    )
    parser.add_argument(
        "--vrf_count",
        type=int,
        default=100,
        help="Number of unique VRFs to generate (default: 100)",
    )
    parser.add_argument(
        "--prefix_count",
        type=int,
        default=100,
        help="Number of unique prefixes to generate (default: 100)",
    )
    args = parser.parse_args()

    vrfs = generate_unique_vrfs(args.vrf_count)
    save_vrfs_to_json(vrfs, args.vrf_filename)
    print(
        f"{args.vrf_count} unique VRFs have been generated and saved to {args.vrf_filename}"
    )

    prefixes = generate_unique_prefixes(args.prefix_count)
    save_prefixes_to_json(prefixes, args.prefix_filename)
    print(
        f"{args.prefix_count} unique prefixes have been generated and saved to {args.prefix_filename}"
    )
