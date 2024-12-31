import json
import argparse
import random
import pynipap
from pynipap import AuthOptions

# Set NIPAP XMLRPC connection
pynipap.xmlrpc_uri = "http://webadmin:NHTvu1aNFb61Lzy75HxN@192.168.101.20:1337/XMLRPC"
a = AuthOptions({"authoritative_source": "python-nipap"})


def generate_random_vrf(vrf_id):
    name = f"VRF-{random.randint(1, 1000)}"
    rt = f"{random.randint(1, 65535)}:{random.randint(1, 65535)}"  # Ensure rt is in ASN:id format
    description = f"description {random.randint(1, 100)}"
    return {
        "id": vrf_id,  # Add a unique ID to each VRF
        "name": name,
        "rt": rt,
        "description": description,
    }


def generate_random_prefix(vrf_id, vrf_name, possible_subnets):
    prefix = possible_subnets.pop()
    return {
        "prefix": prefix,
        "prefix_length": int(prefix.split("/")[1]),
        "display_prefix": prefix,
        "vrf_id": vrf_id,  # Set the VRF ID correctly
        "vrf_rt": vrf_name.split("-")[1],  # Assuming VRF name format is "VRF-<RT>"
        "vrf_name": vrf_name,
        "description": f"description {random.randint(1, 100)}",
        "comment": f"comment {random.randint(1, 100)}",
        "pool_id": None,
        "pool_name": None,
        "type": "assignment",  # Default type, can be changed as needed
        "status": "active",
        "country": random.choice(["US", "CA", "GB", "DE", "FR"]),
        "order_id": random.randint(1000, 9999),
        "customer_id": random.randint(1000, 9999),
        "vlan": random.choice([10, 20, 30, 40, 50]),
        "tags": [],
        "avps": {},
        "expires": "never",
        "external_key": None,
        "authoritative_source": "script",
        "alarm_priority": "critical",
        "monitor": True,
    }


def generate_possible_subnets():
    return random.sample([f"10.0.{i}.0/24" for i in range(256)], k=256)


def save_to_json(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


def main(vrf_file, prefix_file, vrf_count, prefix_count):
    vrfs = []
    vrf_set = set()
    for vrf_id in range(1, vrf_count + 1):  # Generate unique IDs for VRFs
        while True:
            vrf = generate_random_vrf(vrf_id)
            if vrf["rt"] not in vrf_set:
                vrf_set.add(vrf["rt"])
                vrfs.append(vrf)
                break

    save_to_json(vrfs, vrf_file)
    print(f"{vrf_count} unique VRFs have been generated and saved to {vrf_file}")

    possible_subnets = generate_possible_subnets()
    prefixes = []
    for vrf in vrfs:
        vrf_id = vrf["id"]  # Use the unique ID assigned to each VRF
        vrf_name = vrf["name"]
        for _ in range(prefix_count // vrf_count):
            if not possible_subnets:
                possible_subnets = generate_possible_subnets()
            prefix = generate_random_prefix(vrf_id, vrf_name, possible_subnets)
            prefixes.append(prefix)

    save_to_json(prefixes, prefix_file)
    print(
        f"{prefix_count} unique prefixes have been generated and saved to {prefix_file}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate and add VRFs and Prefixes from JSON files."
    )
    parser.add_argument("vrf_filename", type=str, help="Output JSON file name for VRFs")
    parser.add_argument(
        "prefix_filename", type=str, help="Output JSON file name for prefixes"
    )
    parser.add_argument(
        "--vrf_count",
        type=int,
        default=3,
        help="Number of unique VRFs to generate (default: 3)",
    )
    parser.add_argument(
        "--prefix_count",
        type=int,
        default=100,
        help="Number of unique prefixes to generate (default: 1500)",
    )
    args = parser.parse_args()

    main(args.vrf_filename, args.prefix_filename, args.vrf_count, args.prefix_count)
