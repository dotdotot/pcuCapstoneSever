from fastapi import FastAPI
from requests import Session
from fastapi.params import Depends
from starlette.responses import RedirectResponse
from consts import JWT_SECRET, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES
from datetime import datetime, timedelta

import bcrypt
import models, schemas, webMethod, androidMethod, hardwareMethod
import uvicorn
import jwt

from db import enigne, get_db

models.Base.metadata.create_all(bind=enigne)

app = FastAPI()

@app.get("/")
def main():
    return RedirectResponse(url="/docs")

async def is_login_id_exist(login_id_str: str,db:Session = Depends(get_db)):
    #같은 id가 있는지 확인하는 함수
    get_login_id = db.query(models.User.login_id).filter_by(login_id=login_id_str).first()
    if get_login_id:
        return True
    else:
        return False


# access token 생성
def create_access_token(*, data: dict, expires_delta: int = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(*, data: dict, expires_delta: int = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


#회원가입
@app.post("/register/{login_id}/{login_pw}/{nickname}/{name}/{email}/{phone}",status_code=200)
async def register(login_id: str, login_pw:str, nickname: str, name: str, email:str, phone: str,db:Session = Depends(get_db)):
    """
    회원가입 API
    """

    id_exist = db.query(models.User.login_id).filter_by(login_id=login_id).first()
    nickname_exist = db.query(models.User.nickname).filter_by(nickname=nickname).first()
    name_exist = db.query(models.User.name).filter_by(name=name).first()
    email_exist = db.query(models.User.email).filter_by(email=email).first()
    phone_exist = db.query(models.User.phone).filter_by(phone=phone).first()

    if not login_id or not login_pw:
        return {"result":"FALSE"}
    if id_exist:
        return {"result":"FALSE"}
    if nickname_exist:
        return {"result":"FALSE"}
    if name_exist:
        return {"result":"FALSE"}
    if email_exist:
        return {"result":"FALSE"}
    if phone_exist:
        return {"result":"FALSE"}
    
    hash_pw = bcrypt.hashpw(login_pw.encode("utf-8"), bcrypt.gensalt())
    models.User.create(db, auto_commit=True, login_pw=hash_pw, login_id=login_id, nickname=nickname, name=name, email=email,phone=phone)

    return {"result":"TRUE"}


#로그인
@app.get("/login/{login_id}/{login_pw}",status_code=200)
async def login(login_id:str, login_pw:str, db:Session = Depends(get_db)):

    is_exist = await is_login_id_exist(login_id,db)
    db_user_info = db.query(models.User).filter_by(login_id=login_id).first() 

    if is_exist == True: #db에 id가 있어야 비밀번호 확인
        is_verified = bcrypt.checkpw(login_pw.encode("utf-8"),db_user_info.login_pw.encode("utf-8"))
    else:
        return {"result":"FALSE"}

    if is_exist == True and is_verified == True: 
        token = dict(Authorization=f"Bearer {create_access_token(data=schemas.UserToken.from_orm(db_user_info).dict(exclude={'login_pw'}),)}")
        #models.Token.create(db,auto_commit=True,user_id = db_user_info.id,access_token = token)
        return {"result":"TRUE"}
    elif is_verified == False or is_exist == False:
        return {"result":"FALSE"}
    else:
        return {"result":"FALSE"}

   
app.include_router(androidMethod.router)
app.include_router(webMethod.router)
app.include_router(hardwareMethod.router)

if __name__  == '__main__':
    uvicorn.run(app="main:app", 
                host="203.250.133.171", #192.168.219.106 203.250.133.171
                port=8000,
                reload=True,
                ssl_keyfile="C:\\Users\\gksek\\capstone\\fastapi\\app\\ssl\\key.pem",
                ssl_certfile="C:\\Users\\gksek\\capstone\\fastapi\\app\\ssl\\cert.pem",
                ) 