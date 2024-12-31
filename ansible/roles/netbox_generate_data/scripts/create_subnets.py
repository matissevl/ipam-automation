import json
import random
import argparse
from ipaddress import ip_network


def generate_possible_subnets():
    """Generate and shuffle possible subnets."""
    return random.sample([f"10.0.{i}.0/24" for i in range(256)], k=256)


def generate_random_subnet(vrf_name, possible_subnets):
    """Generate a random subnet with metadata."""
    prefix = possible_subnets.pop()
    return {
        "prefix": prefix,
        "status": "active",
        "description": f"description {random.randint(1, 100)}",
        "comments": f"comment {random.randint(1, 100)}",
        "vlan": random.choice([10, 20, 30, 40, 50]),
        "vrf": vrf_name,
    }


def generate_child_subnets(parent_subnet, child_count):
    """Generate a specified number of child subnets from the parent."""
    parent_net = ip_network(parent_subnet["prefix"], strict=False)
    child_prefix_length = random.choice(range(26, 31))  # From /26 to /30
    child_subnets = list(parent_net.subnets(new_prefix=child_prefix_length))[
        :child_count
    ]

    return [
        {
            "prefix": str(child),
            "status": parent_subnet["status"],
            "description": parent_subnet["description"],
            "comments": parent_subnet["comments"],
            "vlan": parent_subnet["vlan"],
            "vrf": parent_subnet["vrf"],
        }
        for child in child_subnets
    ]


def main(output_file, total_count, vrfs_file):
    """Main function to generate subnets."""
    # Load VRFs
    with open(vrfs_file, "r") as f:
        vrfs = json.load(f)

    vrf_count = len(vrfs)
    if vrf_count == 0:
        raise ValueError("No VRFs provided in the input file.")

    # Calculate distribution of parent and child subnets
    avg_children_per_parent = 4  # Fixed number of children per parent
    total_parents = total_count // (avg_children_per_parent + 1)
    total_children = total_parents * avg_children_per_parent

    if total_parents * (avg_children_per_parent + 1) != total_count:
        raise ValueError(
            "The total count cannot be evenly distributed with 4 children per parent."
        )

    subnets_per_vrf = total_parents // vrf_count
    leftover_parents = total_parents % vrf_count

    subnets = []
    possible_subnets = generate_possible_subnets()

    for vrf in vrfs:
        vrf_name = vrf["name"]
        current_vrf_parents = subnets_per_vrf + (1 if leftover_parents > 0 else 0)
        leftover_parents -= 1

        for _ in range(current_vrf_parents):
            if not possible_subnets:
                possible_subnets = generate_possible_subnets()
            parent_subnet = generate_random_subnet(vrf_name, possible_subnets)
            subnets.append(parent_subnet)
            subnets.extend(
                generate_child_subnets(parent_subnet, avg_children_per_parent)
            )

    # Write to output file
    with open(output_file, "w") as f:
        json.dump(subnets, f, indent=4)


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Generate random subnets.")
    parser.add_argument(
        "vrfs_file",
        help="The input JSON file containing VRFs",
    )
    parser.add_argument("output_file", help="The output JSON file")
    parser.add_argument(
        "--count",
        type=int,
        default=300,
        help="Total number of subnets to generate (default: 300)",
    )
    args = parser.parse_args()

    # Execute main function
    main(args.output_file, args.count, args.vrfs_file)
