import hashlib
import base64

# The hash string to verify against
hash_string = "pbkdf2_sha256$720000$2X9pNghomZiamFPU3qTLo8$jfk0J3sFx2eENP912smZsu0XPbf+55YyZ1K8yhMqAgw="

# Split the hash string into its components
algorithm, iterations, salt, stored_hash = hash_string.split("$")

# Convert iterations to an integer
iterations = int(iterations)

# The password you want to check
password_to_check = "Ck6tV769O2Zx2Y5xF2mK"

# Convert salt to bytes
salt_bytes = salt.encode("utf-8")

# Hash the input password using PBKDF2 with SHA-256
hashed_password = hashlib.pbkdf2_hmac(
    "sha256", password_to_check.encode("utf-8"), salt_bytes, iterations
)

# Convert the result to a base64 encoded string
generated_hash = base64.b64encode(hashed_password).decode("utf-8").strip()

# Compare the generated hash with the stored hash
if generated_hash == stored_hash:
    print("Password is correct!")
else:
    print("Password is incorrect!")
