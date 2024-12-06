import jwt
import datetime
import os
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from starlette.status import HTTP_401_UNAUTHORIZED
from dotenv import load_dotenv
from config import SECRET_KEY, users

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
api_key_scheme = APIKeyHeader(name="Authorization", auto_error=False)


def get_current_user(token: str = Depends(oauth2_scheme), api_key: str = Depends(api_key_scheme)):

    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            # email = payload['user'].get("email")
            email = payload.get("email")
            print(payload)
            if email is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            user = users.find_one({"email": email})
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return user
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # If JWT validation fails, try to validate using API key
    if api_key:
        api_key = api_key.replace("Bearer ", "")
        user = users.find_one({"api_key": api_key})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    # If neither JWT nor API key is provided/valid
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )