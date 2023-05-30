import bcrypt

def encrypt_password(password):
    hashed = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
    return hashed

def check_password(password, hashed):
    if bcrypt.checkpw(password.encode('utf8'), hashed):
        return True
    else:
        return False