import json
import argparse
import random
import pynipap
import ipaddress
from pynipap import VRF, Pool, Prefix, AuthOptions, NipapDuplicateError

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


def get_vrf_id(vrf_name):
    search_result = VRF.smart_search(vrf_name, a)
    if search_result["result"]:
        return search_result["result"][0].id
    return None


def generate_unique_prefixes(count, vrf_count):
    prefixes = []
    generated_prefixes = set()  # Track generated prefixes to ensure uniqueness
    assignment_prefixes = []  # To track assignment prefixes (/30 or /31)
    countries = ["US", "CA", "GB", "DE", "FR"]
    statuses = ["assigned", "reserved", "quarantine"]
    parent_mask = 16  # Parent subnet mask
    child_masks = list(range(17, 33))  # Subnet masks from /17 to /32
    vlan_ids = [10, 20, 30, 40, 50]
    parent_count = count // len(child_masks)  # Number of /16 subnets needed
    min_assignments = int(count * 0.20)  # 20% of total subnets
    min_hosts = int(count * 0.10)  # 10% of total subnets
    assignment_count = 0
    host_subnet_count = 0

    # Generate prefixes randomly
    for i in range(count):
        # Randomly select a parent prefix for the current subnet
        second_octet = random.randint(0, 255)
        parent_prefix = f"10.{second_octet}.0.0/{parent_mask}"

        if parent_prefix in generated_prefixes:
            continue  # Ensure no duplicate parent prefixes
        generated_prefixes.add(parent_prefix)

        # Randomly select a VRF
        vrf_index = random.randint(0, vrf_count - 1)
        vrf_name = f"Test VRF {vrf_index + 1}"
        vrf_id = get_vrf_id(vrf_name)

        # Randomly choose a child mask
        child_mask = random.choice(child_masks)

        # Subdivide the parent prefix into smaller subnets if needed
        child_prefixes = subnet_subdivision(parent_prefix, child_mask)
        child_prefix = random.choice(child_prefixes)  # Randomly select one child prefix

        # Handle prefix types based on child mask
        if child_mask == 32:
            prefix_type = "host"  # /32 addresses are hosts
            if host_subnet_count >= min_hosts:
                continue  # Limit the number of /32 subnets
            host_subnet_count += 1

            # Ensure a valid assignment prefix exists for this host
            if len(assignment_prefixes) == 0:
                continue  # Skip creating host if no assignment exists yet

            # Check that the host prefix is within the bounds of an existing assignment prefix
            parent_assignment = assignment_prefixes[-1]  # Use the latest assignment
            network = ipaddress.ip_network(parent_assignment["prefix"])
            if ipaddress.ip_address(child_prefix.split("/")[0]) not in network:
                continue  # Skip host if it's not within the assignment

        elif child_mask in [30, 31]:
            prefix_type = "assignment"  # /30 and /31 are assignments
            if assignment_count >= min_assignments:
                continue  # Limit the number of assignments
            assignment_count += 1

            # Add the assignment prefix to the list of assignments
            assignment_prefix_data = {
                "prefix": child_prefix,
                "prefix_length": child_mask,
                "display_prefix": child_prefix,
                "vrf_id": vrf_id,
                "vrf_rt": f"65000:{100 + vrf_index}",
                "vrf_name": vrf_name,
                "description": f"This is an assignment prefix of {parent_prefix}",
                "comment": "",
                "pool_id": None,
                "pool_name": None,
                "type": "assignment",
                "status": random.choice(statuses),
                "country": random.choice(countries),
                "order_id": random.randint(1000, 9999),
                "customer_id": random.randint(1000, 9999),
                "vlan": random.choice(vlan_ids),
                "tags": [],
                "avps": {},
                "expires": "never",
                "external_key": None,
                "authoritative_source": "script",
                "alarm_priority": "critical",
                "monitor": True,
            }

            # Add the assignment prefix to the list
            assignment_prefixes.append(assignment_prefix_data)

        else:
            prefix_type = "reservation"  # Other subnets are reservations

        # Create prefix data
        prefix_data = {
            "prefix": child_prefix,
            "prefix_length": child_mask,
            "display_prefix": child_prefix,
            "vrf_id": vrf_id,
            "vrf_rt": f"65000:{100 + vrf_index}",
            "vrf_name": vrf_name,
            "description": f"This is a {prefix_type} prefix of {parent_prefix}",
            "comment": "",
            "pool_id": None,
            "pool_name": None,
            "type": prefix_type,
            "status": random.choice(statuses),
            "country": random.choice(countries),
            "order_id": random.randint(1000, 9999),
            "customer_id": random.randint(1000, 9999),
            "vlan": random.choice(vlan_ids),
            "tags": [],
            "avps": {},
            "expires": "never",
            "external_key": None,
            "authoritative_source": "script",
            "alarm_priority": "critical",
            "monitor": True,
        }

        # Add the generated prefix to the list
        prefixes.append(prefix_data)

        # Stop if we've generated enough prefixes
        if len(prefixes) >= count:
            break

    return prefixes


def subnet_subdivision(parent_prefix, new_mask):
    """
    Subdivide a parent prefix into smaller subnets of the desired mask.
    """
    network = ipaddress.ip_network(parent_prefix)
    subnets = list(network.subnets(new_prefix=new_mask))
    return [str(subnet) for subnet in subnets]


def save_prefixes_to_json(prefixes, filename):
    with open(filename, "w") as f:
        json.dump(prefixes, f, indent=4)


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

        try:
            prefix.save()
            print(f"Added Prefix {prefix.prefix}")
        except NipapDuplicateError as e:
            print(f"Error adding Prefix {prefix.prefix}: {e}")


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
        help="Number of unique VRFs to generate (default: 100)",
    )
    parser.add_argument(
        "--prefix_count",
        type=int,
        default=1500,
        help="Number of unique prefixes to generate (default: 100)",
    )
    args = parser.parse_args()

    vrfs = generate_unique_vrfs(args.vrf_count)
    save_vrfs_to_json(vrfs, args.vrf_filename)
    print(
        f"{args.vrf_count} unique VRFs have been generated and saved to {args.vrf_filename}"
    )

    add_vrfs_from_json(args.vrf_filename)

    prefixes = generate_unique_prefixes(args.prefix_count, args.vrf_count)
    save_prefixes_to_json(prefixes, args.prefix_filename)
    print(
        f"{args.prefix_count} unique prefixes have been generated and saved to {args.prefix_filename}"
    )

    add_prefixes_from_json(args.prefix_filename)
    print(
        f"VRFs from {args.vrf_filename} and Prefixes from {args.prefix_filename} have been added"
    )

# Count and display the number of VRFs and prefixes in the database
vrf_count = len(VRF.list())
prefix_count = len(Prefix.list())

print(f"Total VRFs: {vrf_count}")
print(f"Total Prefixes: {prefix_count}")
