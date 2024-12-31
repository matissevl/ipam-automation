import hashlib

username = "webadmin"
salt = "xkefMZzg"  # The salt part of the hash
stored_hash = "e8e46d928617c51c54d768853d5bfc1bcfc97703"  # The hashed password

password_to_check = "NHTvu1aNFb61Lzy75HxN"

# Combine salt and password
combined = salt + password_to_check

# Generate the hash using SHA-1
h = hashlib.sha1()
h.update(combined.encode("utf-8"))  # Both salt and password must be encoded to bytes
generated_hash = h.hexdigest()

# Compare the generated hash with the stored hash
if generated_hash == stored_hash:
    print("Password is correct!")
else:
    print("Password is incorrect!")
