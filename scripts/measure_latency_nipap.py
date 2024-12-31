import time
import pynipap
from pynipap import VRF, Prefix, AuthOptions

# NIPAP Configuration
pynipap.xmlrpc_uri = "http://webadmin:NHTvu1aNFb61Lzy75HxN@192.168.101.20:1337/XMLRPC"
auth_options = AuthOptions({"authoritative_source": "python-nipap"})


# Function to measure query performance
def measure_query(query_func, description):
    start = time.perf_counter()
    try:
        result = query_func()
        result_count = len(result) if hasattr(result, "__len__") else 1 if result else 0
    except Exception as e:
        result_count = 0
    end = time.perf_counter()
    print(f"{description}: {end - start:.4f} seconds | Result Count: {result_count}")


# Function to print totals
def print_totals():
    try:
        # Fetch all VRFs and prefixes to get totals
        vrfs = VRF.list({})
        prefixes = Prefix.list({})

        total_vrfs = len(vrfs)
        total_prefixes = len(prefixes)

        print(f"Total VRFs: {total_vrfs}")
        print(f"Total Prefixes: {total_prefixes}")
    except Exception as e:
        pass


# Test queries
def test_queries():
    # Fetch all VRFs
    measure_query(lambda: VRF.list({}), "Fetch All VRFs")
    time.sleep(1)  # Add delay

    # Fetch all Prefixes
    measure_query(lambda: Prefix.list({}), "Fetch All Prefixes")
    time.sleep(1)  # Add delay

    # Lookup a specific prefix (example: 10.0.1.0/24)
    measure_query(
        lambda: Prefix.list({"prefix": "10.0.144.0/24"}), "Single Prefix Lookup"
    )
    time.sleep(1)  # Add delay

    # Lookup a specific VRF (example: test-vrf)
    measure_query(lambda: VRF.list({"name": "VRF-25"}), "Single VRF Lookup")
    time.sleep(1)  # Add delay


# Run the tests
if __name__ == "__main__":
    print_totals()
    test_queries()
