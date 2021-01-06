#pip install pycryptodome
#https://pycryptodome.readthedocs.io/en/latest/src/cipher/classic.html

#ENCRYPTION
import json
from base64 import b64encode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import unpad #for decryption
from base64 import b64decode

plaintext = "Victor Alfonso"
iv_string = "A01731416A017314"    #El iv debe ser 16 bytes long
#print the actual bytes
pt_bytes = bytes(plaintext, 'utf-8')
for i in pt_bytes:
    print(i)
print("")

iv = bytes(iv_string, 'utf-8')

print("plaintext:", plaintext)
key = get_random_bytes(16)
print("key:", key)
cipher = AES.new(key, AES.MODE_CBC, iv)  #Si quitas el iv, se genera random
print("iv:", cipher.iv)
ct_bytes = cipher.encrypt(pad(pt_bytes, AES.block_size))
print("ciphertext in bytes:", ct_bytes)
print("iv_bytes:", cipher.iv)
iv2 = b64encode(cipher.iv).decode('utf-8')
ct = b64encode(ct_bytes).decode('utf-8')
result = json.dumps({'iv':iv2, 'ciphertext':ct})
print(result)


#DECRYPTION
'''cipher2 = AES.new(key, AES.MODE_CBC, iv)
pt = unpad(cipher2.decrypt(ct_bytes), AES.block_size)
print("plaintext:", pt)
'''
try:
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct_bytes), AES.block_size)
    print("The message was: ", pt)
except:
    print("La cagaste")
