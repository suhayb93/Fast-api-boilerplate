from fastapi import APIRouter, Depends
from typing import Annotated
from Models.Users import Users
from routers.auth import verify_user

from routers.auth import oAuth_schema
router = APIRouter()

@router.get('/home')
def homePage(isVrefied: Annotated[bool, Depends(verify_user)]):
    pass
