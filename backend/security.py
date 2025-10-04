from cryptography.fernet import Fernet

# Generate key: key = Fernet.generate_key()
KEY = Fernet.generate_key()
fernet = Fernet(KEY)

def encrypt_data(data: str) -> bytes:
    return fernet.encrypt(data.encode())

def decrypt_data(data: bytes) -> str:
    return fernet.decrypt(data).decode()
	
	