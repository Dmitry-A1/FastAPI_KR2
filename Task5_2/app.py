from fastapi import FastAPI, Response, Cookie, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uuid
import bcrypt
from itsdangerous import Signer, BadSignature

app = FastAPI(title="Signed Cookie Auth API")

SECRET_KEY = "my-super-secret-cryptographic-key"

signer = Signer(SECRET_KEY)

STATIC_USER_UUID = str(uuid.uuid4())

salt = bcrypt.gensalt()
hashed_password = bcrypt.hashpw(b"password123", salt)


users_db = {
    "user123": {
        "user_id": STATIC_USER_UUID,
        "password_hash": hashed_password,
        "profile": {
            "name": "Алексей",
            "email": "user123@example.com",
            "role": "Full-Stack Developer"
        }
    }
}

uuid_to_username = {STATIC_USER_UUID: "user123"}

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/login")
def login(login_data: LoginRequest, response: Response):

    user = users_db.get(login_data.username)

    if not user or not bcrypt.checkpw(login_data.password.encode('utf-8'), user["password_hash"]):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"message": "Invalid credentials"}
        )

    user_id = user["user_id"]

    signed_token = signer.sign(user_id).decode('utf-8')
    response.set_cookie(
        key="session_token",
        value=signed_token,
        httponly=True,
        max_age=3600,
        samesite="lax"
    )

    return {"message": "Успешный вход", "token_preview": signed_token}


@app.get("/profile")
def get_profile(session_token: str | None = Cookie(default=None)):
    if not session_token:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"message": "Unauthorized"}
        )

    try:
        unsigned_user_id_bytes = signer.unsign(session_token)
        user_id = unsigned_user_id_bytes.decode('utf-8')

    except BadSignature:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"message": "Unauthorized"}
        )

    username = uuid_to_username.get(user_id)
    if not username:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"message": "Unauthorized"}
        )

    return users_db[username]["profile"]