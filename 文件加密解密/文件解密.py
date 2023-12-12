from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import os
import py7zr

BASE_PATH = r"C:\Users\11470\Desktop\加密"

def recover_key(shares: list[bytes], last_share_length: int) -> bytes:
    """Use the length of the last share to recover the key."""
    return b''.join(shares[:-1]) + shares[-1][:last_share_length]

def decrypt_file(filename, key):
    with open(filename, 'rb') as f:
        iv = f.read(16)
        ciphertext = f.read()
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    with open(filename[:-4], 'wb') as f:
        f.write(plaintext)
    os.remove(filename)

with py7zr.SevenZipFile(os.path.join(BASE_PATH, 'keys.7z'), mode='r', password='1021') as z:
    z.extractall()

shares = []
for i in range(3):
    with open(f"key{i + 1}.key", "rb") as f:
        shares.append(f.read())

with open("last_share_length.txt", "r") as f:
    last_share_length = int(f.read())  # Read the length of the last share from the file

key = recover_key(shares, last_share_length)



if len(key) != 32:
    raise ValueError("Incorrect key length")

for root, dirs, files in os.walk(BASE_PATH):
    for file in files:
        if file.endswith('.enc'):
            decrypt_file(os.path.join(root, file), key)
