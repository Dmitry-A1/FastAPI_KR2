import time
import uuid
import bcrypt
from fastapi import FastAPI, Response, Cookie, status
from pydantic import BaseModel
from itsdangerous import Signer, BadSignature

app = FastAPI()

SECRET_KEY = "ultra-secure-secret-key-for-sessions"
signer = Signer(SECRET_KEY)

STATIC_USER_UUID = str(uuid.uuid4())
hashed_pw = bcrypt.hashpw(b"password123", bcrypt.gensalt())
users_db = {
    "user123": {
        "user_id": STATIC_USER_UUID,
        "password_hash": hashed_pw,
        "profile": {"name": "Alex", "role": "Senior Developer"}
    }
}
uuid_to_username = {STATIC_USER_UUID: "user123"}


class LoginRequest(BaseModel):
    username: str
    password: str


def create_session_cookie(user_id: str):
    current_time = str(int(time.time()))
    payload = f"{user_id}.{current_time}"
    return signer.sign(payload).decode('utf-8')


@app.post("/login")
def login(login_data: LoginRequest, response: Response):
    user = users_db.get(login_data.username)
    if not user or not bcrypt.checkpw(login_data.password.encode(), user["password_hash"]):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "Invalid credentials"}

    signed_token = create_session_cookie(user["user_id"])
    response.set_cookie(
        key="session_token",
        value=signed_token,
        httponly=True,
        max_age=300,
        samesite="lax"
    )
    return {"message": "Logged in"}


@app.get("/profile")
def get_profile(response: Response, session_token: str | None = Cookie(default=None)):
    if not session_token:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "Unauthorized"}

    try:
        unsigned_payload = signer.unsign(session_token).decode('utf-8')
        parts = unsigned_payload.split('.')
        if len(parts) != 2:
            raise ValueError()

        user_id, timestamp_str = parts
        last_activity = int(timestamp_str)
    except (BadSignature, ValueError):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "Invalid session"}

    current_time = int(time.time())
    elapsed_time = current_time - last_activity

    if elapsed_time > 300:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "Session expired"}

    if 180 <= elapsed_time < 300:
        new_token = create_session_cookie(user_id)
        response.set_cookie(
            key="session_token",
            value=new_token,
            httponly=True,
            max_age=300,
            samesite="lax"
        )

    username = uuid_to_username.get(user_id)
    if not username:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "Invalid session"}

    return users_db[username]["profile"]