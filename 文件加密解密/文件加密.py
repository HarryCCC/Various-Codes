from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import os
import py7zr

BASE_PATH = r"C:\Users\11470\Desktop\加密"

def split_key(key: bytes, n: int) -> tuple[list[bytes], int]:
    """Split the key into n parts."""
    total_length = len(key)
    share_length = total_length // n
    remaining = total_length % n
    
    shares = [key[i:i+share_length] for i in range(0, total_length - share_length, share_length)]
    
    # Add the remaining bytes to the last share
    last_share = shares[-1] + key[-remaining:]
    shares[-1] = last_share
    
    return shares, len(last_share)



def encrypt_file(filename, key):
    cipher = AES.new(key, AES.MODE_CBC)
    with open(filename, 'rb') as f:
        plaintext = f.read()
    ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
    with open(filename + ".enc", 'wb') as f:
        f.write(cipher.iv)
        f.write(ciphertext)
    os.remove(filename)

key = get_random_bytes(32)

for root, dirs, files in os.walk(BASE_PATH):
    for file in files:
        if not file.endswith('.py'):
            encrypt_file(os.path.join(root, file), key)

shares, last_share_length = split_key(key, 3)

for i, share in enumerate(shares):
    with open(f"key{i + 1}.key", "wb") as f:
        f.write(share)

with open("last_share_length.txt", "w") as f:
    f.write(str(last_share_length))  # Save the length of the last share to a file

with py7zr.SevenZipFile(os.path.join(BASE_PATH, 'keys.7z'), mode='w', password='1021') as z:
    for i in range(3):
        z.write(f"key{i + 1}.key", f"key{i + 1}.key")
        os.remove(f"key{i + 1}.key")
    z.write("last_share_length.txt", "last_share_length.txt")
    os.remove("last_share_length.txt")
