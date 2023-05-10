import hashlib

def hash_pwd(password):
    password = password.encode()
    salt = 'salt'.encode()
    dk = hashlib.pbkdf2_hmac('sha256', password, salt, 100000)
    return dk.hex()
