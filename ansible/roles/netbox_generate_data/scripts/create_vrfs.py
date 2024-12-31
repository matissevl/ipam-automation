import json
import random
import argparse


def generate_random_vrf():
    name = f"VRF-{random.randint(1, 1000)}"
    rd = f"{random.randint(1, 65535)}:{random.randint(1, 65535)}"
    description = f"description {random.randint(1, 100)}"
    return {
        "name": name,
        "rd": rd,
        "description": description,
    }


# Set up argument parser
parser = argparse.ArgumentParser(description="Generate random VRFs.")
parser.add_argument("output_file", help="The output JSON file")
parser.add_argument(
    "--count",
    type=int,
    default=5,
    help="Number of VRFs to generate (default: 5)",
)

args = parser.parse_args()

vrfs = []
vrf_set = set()  # Set to track unique VRFs

for _ in range(args.count):
    while True:
        vrf = generate_random_vrf()
        if vrf["rd"] not in vrf_set:
            vrf_set.add(vrf["rd"])
            vrfs.append(vrf)
            break

with open(args.output_file, "w") as f:
    json.dump(vrfs, f, indent=4)
