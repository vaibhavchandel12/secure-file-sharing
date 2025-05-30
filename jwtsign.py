import time
import jwt
from fastapi import HTTPException
from pydantic import BaseModel
import secrets

# Generate a secure random secret for signing the token
JWT_SECRET = secrets.token_hex(16)
JWT_ALGORITHM = "HS256"

print("JWT_SECRET:", JWT_SECRET)  # For debugging only

def sign(email):
    payload = {
        "email": email,
        # You can optionally add an expiration like this:
        # "exp": time.time() + 3600
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

# -------------------------------
# Function to decode/verify JWT
# -------------------------------
def decode(token):
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")