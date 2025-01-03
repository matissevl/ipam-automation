import json
import random
import argparse
import ipaddress


def generate_ip_pool(subnets):
    """Precompute available IPs for each subnet."""
    ip_pool = {}
    for subnet in subnets:
        network = ipaddress.ip_network(subnet["prefix"])
        ip_pool[subnet["prefix"]] = list(network.hosts())
    return ip_pool


def evenly_distribute_ips(ip_pool, total_count):
    """Calculate the number of IPs to generate per subnet."""
    total_hosts = sum(len(hosts) for hosts in ip_pool.values())
    if total_hosts < total_count:
        raise ValueError(
            "Not enough IPs in the provided subnets to generate the requested count."
        )

    distribution = {}
    remaining_count = total_count

    for prefix, hosts in ip_pool.items():
        proportion = len(hosts) / total_hosts
        allocation = round(proportion * total_count)
        distribution[prefix] = min(
            allocation, len(hosts)
        )  # Limit allocation to available hosts
        remaining_count -= distribution[prefix]

    # Adjust any remainder by distributing 1 IP at a time
    sorted_subnets = sorted(ip_pool.keys(), key=lambda p: len(ip_pool[p]), reverse=True)
    for prefix in sorted_subnets:
        if remaining_count <= 0:
            break
        if distribution[prefix] < len(ip_pool[prefix]):
            distribution[prefix] += 1
            remaining_count -= 1

    return distribution


def generate_random_ips(ip_pool, allocation, ip_set, vrf_name):
    """Generate IP addresses based on allocation."""
    ip_addresses = []
    for prefix, count in allocation.items():
        for _ in range(count):
            hosts = ip_pool[prefix]
            address = str(hosts.pop(random.randrange(len(hosts))))
            ip_set.add(address)
            ip_addresses.append(
                {
                    "address": address + f"/{ipaddress.ip_network(prefix).prefixlen}",
                    "status": "active",
                    "dns_name": f"host{random.randint(1, 100)}.example.com",
                    "description": f"description {random.randint(1, 100)}",
                    "vrf": vrf_name,
                }
            )
    return ip_addresses


# Set up argument parser
parser = argparse.ArgumentParser(description="Generate random IP addresses.")
parser.add_argument("vrfs_file", help="The input JSON file with VRFs")
parser.add_argument("subnets_file", help="The input JSON file with subnets")
parser.add_argument("output_file", help="The output JSON file")
parser.add_argument(
    "--count",
    type=int,
    default=500,
    help=" Total number of IP addresses to generate (default: 2000)",
)

args = parser.parse_args()

# Load input files
with open(args.subnets_file, "r") as f:
    subnets = json.load(f)

with open(args.vrfs_file, "r") as f:
    vrfs = json.load(f)

if not vrfs:
    raise ValueError("No VRFs provided in the input file.")

ip_pool = generate_ip_pool(subnets)  # Precompute IPs
total_count = args.count
ip_set = set()  # Set to track unique IP addresses
ip_addresses = []

# Calculate number of IPs to generate per VRF
num_vrfs = len(vrfs)
ips_per_vrf = total_count // num_vrfs
remaining_ips = total_count % num_vrfs  # Handle any remainder

# Generate IP addresses for each VRF
for i, vrf in enumerate(vrfs):
    vrf_name = vrf["name"]
    target_count = ips_per_vrf + (1 if i < remaining_ips else 0)  # Distribute remainder
    allocation = evenly_distribute_ips(ip_pool, target_count)  # Per-subnet allocation
    vrf_ips = generate_random_ips(ip_pool, allocation, ip_set, vrf_name)
    ip_addresses.extend(vrf_ips)

    print(f"Generated {len(vrf_ips)}/{target_count} IPs for VRF {vrf_name}")

# Save the output to a JSON file
with open(args.output_file, "w") as f:
    json.dump(ip_addresses, f, indent=4)

# Print the number of generated IP addresses and the calculation
total_ip_addresses = len(ip_addresses)
print(f"Total number of generated IP addresses: {total_ip_addresses}")
print(f"Expected total: {total_count}")
if total_ip_addresses != total_count:
    print(
        "Warning: The actual total does not match the expected total. Check for uniqueness constraints or subnet exhaustion."
    )
