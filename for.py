from cryptography.fernet import Fernet

# Generate a key
encryption_key = Fernet.generate_key()
print(encryption_key.decode())  # Print the key as a string