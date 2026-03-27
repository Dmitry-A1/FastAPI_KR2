
from fastapi import FastAPI, Response, Cookie, HTTPException, status
from pydantic import BaseModel
import uuid

app = FastAPI()

user_bd = {
    "user123":{
        "password":"123123",
        "profile":{
            "name":"Пупкин Иван",
            "email":"user@test.com",
            "role":"admin"
        }
    }
}

session_db = {}

class LoginRequest(BaseModel):
    username: str
    password: str

app.post("/login")
def login(login_data: LoginRequest, response: Response):
    user = user_bd.get(login_data.username)

    if not user or user["password"] != login_data.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Неверное имя пользователя")

    session_token = str(uuid.uuid4())

    session_db[session_token] = login_data.username

    response.set_cookie(
        key=session_token,
        value=session_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=3600
    )
    return {"message":"Успешный вход"}

@app.get("/user")
def get_user(session_token: str | None = Cookie(default = None)):
    if not session_token or session_token not in session_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )

    username = session_db[session_token]

    user_profile = user_bd[username]["profile"]
    return {"username":username, "profile":user_profile}