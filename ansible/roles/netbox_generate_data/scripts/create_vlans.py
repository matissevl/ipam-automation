import json
import random
import argparse


def generate_random_vlan(available_vids):
    vid = random.choice(available_vids)
    available_vids.remove(vid)
    name = f"VLAN-{vid}"
    status = random.choice(["active", "reserved", "deprecated"])
    return {
        "vid": vid,
        "name": name,
        "status": status,
    }


# Set up argument parser
parser = argparse.ArgumentParser(description="Generate random VLANs.")
parser.add_argument("output_file", help="The output JSON file")

args = parser.parse_args()

available_vids = [10, 20, 30, 40, 50]
vlans = []
for _ in range(len(available_vids)):
    vlans.append(generate_random_vlan(available_vids))

with open(args.output_file, "w") as f:
    json.dump(vlans, f, indent=4)
