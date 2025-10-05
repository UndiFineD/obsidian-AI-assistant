from cryptography.fernet import Fernet

# Generate key: key = Fernet.generate_key()
# For production, use environment variable or secure key management
KEY = b'ZmDfcTF7_60GrrY167zsiPd67pEvs0aGOv2oasOM1Pg='  # Example key - replace in production
fernet = Fernet(KEY)

def encrypt_data(data: str) -> bytes:
    return fernet.encrypt(data.encode())

def decrypt_data(data: bytes) -> str:
    return fernet.decrypt(data).decode()

	
