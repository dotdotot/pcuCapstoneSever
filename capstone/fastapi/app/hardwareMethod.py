from fastapi import APIRouter
from requests import Session
from fastapi.params import Depends
from sqlalchemy import desc
from db import get_db

import models, schemas

router = APIRouter(prefix="/hardwareMethod",tags=["hardwareMethod"])

@router.get("/test",status_code=200)
async def test():
    return {"message":"testOK"}

