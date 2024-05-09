import jwt
import os
from datetime import datetime

SECRET_KEY = os.environ['APP_SECRET']  # Replace with your actual secret key
ALGORITHM = "HS256"


def create_jwt(username: str):
    # Define the JWT payload without the `exp` field
    payload = {
        "sub": username,  # Subject of the token
        "iat": datetime.utcnow(),  # Issued At: Time when the JWT was issued
        # Note: Expiration (exp) is omitted
    }

    # Encode the payload to generate the JWT
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


# Example usage
username = "zh3036"
token = create_jwt(username)
print(f"JWT for {username}: {token}")
