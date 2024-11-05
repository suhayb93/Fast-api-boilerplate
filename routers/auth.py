from fastapi import APIRouter, Depends, HTTPException, status, Body
from pydantic import BaseModel, Field
from typing import Annotated
from sqlalchemy.orm import Session
from Database import get_db
from Models.Users import Users
from passlib.hash import bcrypt
import jwt
from jwt.exceptions import DecodeError, InvalidTokenError, InvalidSignatureError, ExpiredSignatureError
from datetime import timedelta, datetime, UTC
from fastapi.security import OAuth2PasswordBearer
from redis_configs import redis_interface
from redis.exceptions import ConnectionError
import json
import os

token_exp = int(os.getenv('JWT_EXPIRES'))
router = APIRouter()

ALGORITHM = os.getenv('JWT_ALGORITHM')
SECRET = os.getenv('JWT_SECRET')

oAuth_schema = OAuth2PasswordBearer(tokenUrl='auth/token')

class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=4)


def create_token(user: Users, secret_key, algorithm, expires_delta: timedelta):
    expires = datetime.now(UTC) + expires_delta
    idle_time = os.getenv('IDLE_TIME')
    payload = {'sub': user.id, 'name': user.username, 'role': user.role, 'exp': expires, 'idlTime': idle_time }
    return jwt.encode(payload, algorithm=algorithm, key=secret_key)


def block_token(token, user_id, expiration):
    payload = {
        "user_id": user_id,
        "status": 'block'
    }
    exp_timestamp = datetime.fromtimestamp(expiration)
    current_timestamp = datetime.now()
    timedate_delta = exp_timestamp - current_timestamp
    _payload = json.dumps(payload)
    try:
        redis_interface.set(token, _payload, ex=int(timedate_delta.total_seconds()))
    except ConnectionError:
        print("redis connection failed")


def check_token_validity(token, user_id):
    try:
        payload_text = redis_interface.get(token)
        if redis_interface and payload_text is not None:
            payload = json.loads(payload_text)
            return payload.get('user_id') == user_id and payload.get('status') != 'block'
        return True
    except ConnectionError:
        print('redis connection failed')
        return True

def get_current_user(token: Annotated[Session, Depends(oAuth_schema)],
                db: Annotated[Session, Depends(get_db)]):

    try:
        payload = jwt.decode(token, algorithms=[ALGORITHM], key=SECRET, options={"verify_exp": True})
        user_id = payload['sub']

        user = db.query(Users).filter(Users.id == user_id).first()
        if check_token_validity(token, user_id) is False:
            raise InvalidTokenError

        return user
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Session time out')
    except (InvalidSignatureError, InvalidTokenError, DecodeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid Token')



def verify_user(user: Annotated[Users, Depends(get_current_user)]):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized")
    return True

@router.post('/token')
def login(payload: LoginRequest,
          db: Annotated[Session, Depends(get_db)]):
    username = payload.username
    password = payload.password

    user = db.query(Users).filter(Users.username == username).first()

    if user is not None and bcrypt.verify(password, user.password_hash):
        return {
            'access_token': create_token(user, SECRET, ALGORITHM, timedelta(minutes=token_exp)),
            'token_type': 'bearer'
        }
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='username or password is wrong')


@router.post('/logout')
def logout(token: Annotated[Session, Depends(oAuth_schema)],
           payload=Body()):
    user_id = payload['id']
    exp = payload['exp']
    block_token(token, user_id, exp)
    return True

