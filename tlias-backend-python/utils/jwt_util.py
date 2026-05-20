import jwt
from datetime import datetime, timedelta, timezone

SECRET = 'tlias-secret-key-2024-project-intelligent-agriculture'
EXPIRATION_HOURS = 24


def generate_token(user_id: int, name: str) -> str:
    payload = {
        'userId': user_id,
        'name': name,
        'exp': datetime.now(timezone.utc) + timedelta(hours=EXPIRATION_HOURS),
    }
    return jwt.encode(payload, SECRET, algorithm='HS256')


def verify_token(token: str) -> dict:
    return jwt.decode(token, SECRET, algorithms=['HS256'])
