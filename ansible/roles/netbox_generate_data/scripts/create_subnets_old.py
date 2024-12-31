import json
import random
import argparse


def generate_possible_subnets():
    subnets = [f"10.0.{i}.0/24" for i in range(256)]
    random.shuffle(subnets)
    return subnets


def generate_random_subnet(vrf_name, possible_subnets):
    prefix = possible_subnets.pop()
    status = "active"
    description = f"description {random.randint(1, 100)}"
    comments = f"comment {random.randint(1, 100)}"
    vlan = random.choice([10, 20, 30, 40, 50])
    return {
        "prefix": prefix,
        "status": status,
        "description": description,
        "comments": comments,
        "vlan": vlan,
        "vrf": vrf_name,
    }


def generate_child_subnets(parent_subnet, num_child_subnets):
    prefix, _ = parent_subnet["prefix"].split("/")
    base_ip = prefix.split(".")
    base_ip = list(map(int, base_ip))
    child_subnets = []

    for i in range(num_child_subnets):
        subnet_size = random.choice([26, 27, 28, 29, 30])
        child_prefix = f"{base_ip[0]}.{base_ip[1]}.{base_ip[2]}.{i * (2 ** (32 - subnet_size))}/{subnet_size}"
        child_subnets.append(
            {
                "prefix": child_prefix,
                "status": parent_subnet["status"],
                "description": parent_subnet["description"],
                "comments": parent_subnet["comments"],
                "vlan": parent_subnet["vlan"],
                "vrf": parent_subnet["vrf"],
            }
        )

    return child_subnets


# Set up argument parser
parser = argparse.ArgumentParser(description="Generate random subnets.")
parser.add_argument("output_file", help="The output JSON file")
parser.add_argument(
    "--count",
    type=int,
    default=10,
    help="Number of subnets to generate (default: 100)",
)
parser.add_argument(
    "--vrfs_file",
    help="The input JSON file containing VRFs",
)
parser.add_argument(
    "--child_count",
    type=int,
    default=4,
    help="Number of child subnets to generate per parent subnet (default: 4)",
)

args = parser.parse_args()

# Load VRFs from file
with open(args.vrfs_file, "r") as f:
    vrfs = json.load(f)

subnets = []

possible_subnets = generate_possible_subnets()

for vrf in vrfs:
    vrf_name = vrf["name"]
    for _ in range(args.count):
        if not possible_subnets:
            possible_subnets = generate_possible_subnets()
        parent_subnet = generate_random_subnet(vrf_name, possible_subnets)
        subnets.append(parent_subnet)
        for child_subnet in generate_child_subnets(parent_subnet, args.child_count):
            subnets.append(child_subnet)

with open(args.output_file, "w") as f:
    json.dump(subnets, f, indent=4)

# Print the number of generated subnets and the calculation
total_subnets = len(subnets)
print(f"Total number of generated subnets: {total_subnets}")
print(
    f"Calculation: {len(vrfs)} VRFs * {args.count} parent subnets per VRF * (1 parent + {args.child_count} child subnets) = {total_subnets}"
)
