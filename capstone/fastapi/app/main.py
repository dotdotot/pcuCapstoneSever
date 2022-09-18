from fastapi import FastAPI
from requests import Session
from fastapi.params import Depends
from typing import List
from starlette.responses import RedirectResponse
from consts import JWT_SECRET, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import datetime, timedelta
from starlette.responses import JSONResponse
from fastapi.security import APIKeyHeader

import bcrypt
import models, schemas
import uvicorn
import jwt

from db import SessionLocal, enigne

models.Base.metadata.create_all(bind=enigne)

app = FastAPI()

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get("/")
def main():
    return RedirectResponse(url="/docs/")


#회원가입
@app.post("/register/",status_code=200,response_model=schemas.Token)
async def register(reg_info: schemas.User,db:Session = Depends(get_db)):
    """
    회원가입 API
    """
    is_exist = await is_login_id_exist(reg_info.login_id,db) 
    if not reg_info.login_id or not reg_info.login_pw:
        return JSONResponse(status_code=400, content=dict(msg="id and pw must be provided"))
    if not is_exist:
        return JSONResponse(status_code=400,content=dict(msg="id already registered"))
    
    hash_pw = bcrypt.hashpw(reg_info.login_pw.encode("utf-8"), bcrypt.gensalt())
    new_user = models.User.create(db, auto_commit=True, login_pw=hash_pw, login_id=reg_info.login_id, nickname=reg_info.nickname, name=reg_info.name, email=reg_info.email,phone=reg_info.phone)
    token = dict(Authorization=f"Bearer {create_access_token(data=reg_info.from_orm(new_user).dict(exclude={'login_pw'}),)}")
    
    return token


# 로그인
@app.post("/login/",status_code=200,response_model=schemas.Token)
async def login(user_info: schemas.UserLogin, db:Session = Depends(get_db)):
    is_exist = await is_login_id_exist(user_info.login_id,db)
    if not user_info.login_id or not user_info.login_pw:
        return JSONResponse(status_code=400, content=dict(msg="ID and PW must be provided"))
    if not is_exist:
        return JSONResponse(status_code=400, content=dict(msg="NO_MATCH_USER"))
    db_user_info: models.User = get_user_by_login_id(db, login_id=user_info.login_id)
    is_verified = bcrypt.checkpw(user_info.login_pw.encode("utf-8"), db_user_info.login_pw.encode("utf-8"))
    if not is_verified:
            return JSONResponse(status_code=400, content=dict(msg="NO_MATCH_USER"))
    token = dict(Authorization=f"Bearer {create_access_token(data=schemas.UserToken.from_orm(db_user_info).dict(exclude={'login_pw'}),)}")
    
    return token


def get_user_by_login_id(db: Session, login_id: str):
    return db.query(models.User).filter(models.User.login_id == login_id).first()

async def is_login_id_exist(login_id: str,db:Session = Depends(get_db)):
    #같은 id가 있는지 확인하는 함수
    get_login_id = db.query(models.User).filter_by(login_id=login_id)
    if get_login_id:
        return True
    return False

# token 생성
def create_access_token(*, data: dict, expires_delta: int = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

#방추가
@app.post("/addRoom/", response_model=schemas.RoomList)
def add_room(entrada: schemas.RoomList, db:Session = Depends(get_db)):
    new_room = models.RoomList.create(db, auto_commit=True, 
                                    user_id = entrada.user_id,
                                    room_name = entrada.room_name)
    
    db.add(new_room)
    db.commit()

    return new_room


# 특정방 찾기
@app.get("/findRoom/",response_model=schemas.RoomList)
def find_room(room_name:str,db:Session=Depends(get_db)):
    room = db.query(models.RoomList).filter_by(room_name=room_name).first()

    return room

# 특정방 삭제 /오류
@app.delete('/deleteRoom/')
def delete_room(room_name:str, db: Session=Depends(get_db)):
    room = db.query(models.RoomList).get(room_name==room_name)

    db.delete(room)
    db.commit()
    db.close()

    return {'200 Successful Response'}


#방 정보 생성 / 아니 왜 room_id랑 temp밖에 안나오냐고 시벌
@app.post("/addRoomInfo/", response_model=schemas.Room_Info)
def add_room(entrada: schemas.Room_Info, db:Session = Depends(get_db)):
    new_roomInfo = models.Room_Management.create(db, auto_commit=True, 
                                    room_id = entrada.room_id,
                                    temp = entrada.temp,
                                    humitiy= entrada.humitiy,
                                    finedust= entrada.finedust,
                                    ledcolor= entrada.ledcolor)
    db.add(new_roomInfo)
    db.commit()

    return new_roomInfo


if __name__  == '__main__':
    uvicorn.run(app="main:app", 
                host="192.168.219.106", #203.250.133.171 192.168.219.106
                port=8000,
                reload=True,
                ssl_keyfile="C:\\Users\\gksek\\capstone\\fastapi\\app\\ssl\\key.pem",
                ssl_certfile="C:\\Users\\gksek\\capstone\\fastapi\\app\\ssl\\cert.pem",
                ) 