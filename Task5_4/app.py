import re
from typing import Annotated
from fastapi import FastAPI, Header, HTTPException, status

app = FastAPI()


LANGUAGE_FORMAT_REGEX = r"^[a-zA-Z]{2,8}(-[a-zA-Z0-9]{2,8})?(\s*,\s*[a-zA-Z]{2,8}(-[a-zA-Z0-9]{2,8})?(\s*;\s*q=[0-9.]+)?)*$"


@app.get("/headers")
def get_request_headers(
        user_agent: Annotated[str | None, Header(default=None)] = None,
        accept_language: Annotated[str | None, Header(default=None)] = None
):
    if not user_agent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing 'User-Agent' header"
        )

    if not accept_language:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing 'Accept-Language' header"
        )

    if not re.match(LANGUAGE_FORMAT_REGEX, accept_language):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid 'Accept-Language' format"
        )

    return {
        "User-Agent": user_agent,
        "Accept-Language": accept_language
    }