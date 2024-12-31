import pynipap
from pynipap import VRF, Pool, Prefix, AuthOptions
import json
import argparse

pynipap.xmlrpc_uri = "http://webadmin:NHTvu1aNFb61Lzy75HxN@192.168.101.20:1337/XMLRPC"

a = AuthOptions({"authoritative_source": "python-nipap"})


def save_vrfs_to_json(vrfs, filename):
    with open(filename, "w") as f:
        json.dump(vrfs, f, indent=4)


def read_vrfs_from_json(filename):
    with open(filename, "r") as f:
        vrfs = json.load(f)
    return vrfs


def add_vrfs_from_json(filename):
    vrfs = read_vrfs_from_json(filename)
    existing_vrfs = {vrf.name for vrf in VRF.list()}
    existing_rts = {vrf.rt for vrf in VRF.list()}
    for vrf_data in vrfs:
        if vrf_data["name"] in existing_vrfs or vrf_data["rt"] in existing_rts:
            print(
                f"VRF {vrf_data['name']} or RT {vrf_data['rt']} already exists, skipping..."
            )
            continue
        vrf = VRF()
        vrf.name = vrf_data["name"]
        vrf.rt = vrf_data["rt"]
        vrf.description = vrf_data["description"]
        vrf.save()
        print(f"Added VRF {vrf.name}")


def read_prefixes_from_json(filename):
    with open(filename, "r") as f:
        prefixes = json.load(f)
    return prefixes


def add_prefixes_from_json(filename):
    prefixes = read_prefixes_from_json(filename)
    existing_prefixes = {prefix.prefix for prefix in Prefix.list()}
    for prefix_data in prefixes:
        if prefix_data["prefix"] in existing_prefixes:
            print(f"Prefix {prefix_data['prefix']} already exists, skipping...")
            continue
        prefix = Prefix()
        prefix.prefix = prefix_data["prefix"]
        prefix.vrf = VRF.get(prefix_data["vrf_id"])
        prefix.description = prefix_data["description"]
        prefix.comment = prefix_data["comment"]
        prefix.node = prefix_data.get("node")  # Use get method to handle missing key
        prefix.pool = (
            Pool.get(prefix_data["pool_id"]) if prefix_data["pool_id"] else None
        )
        prefix.type = prefix_data["type"]
        prefix.status = prefix_data["status"]
        prefix.country = prefix_data["country"]
        prefix.order_id = prefix_data["order_id"]
        prefix.customer_id = prefix_data["customer_id"]
        prefix.vlan = prefix_data["vlan"]
        prefix.tags = prefix_data["tags"]
        prefix.avps = prefix_data["avps"]
        prefix.expires = prefix_data["expires"]
        prefix.external_key = prefix_data["external_key"]
        prefix.authoritative_source = prefix_data["authoritative_source"]
        prefix.alarm_priority = prefix_data["alarm_priority"]
        prefix.monitor = prefix_data["monitor"]
        prefix.save()
        print(f"Added Prefix {prefix.prefix}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Add VRFs and Prefixes from JSON files."
    )
    parser.add_argument("vrf_filename", type=str, help="Input VRF JSON file name")
    parser.add_argument("subnet_filename", type=str, help="Input Subnet JSON file name")
    args = parser.parse_args()

    add_vrfs_from_json(args.vrf_filename)
    add_prefixes_from_json(args.subnet_filename)
    print(
        f"VRFs from {args.vrf_filename} and Prefixes from {args.subnet_filename} have been added"
    )

# VRF’s, subnetten, VLAN’s en IP-adressen
