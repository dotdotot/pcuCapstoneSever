from fastapi import FastAPI, Request
from requests import Session
from fastapi.params import Depends
from typing import List
from starlette.responses import RedirectResponse
from consts import JWT_SECRET, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES
from datetime import datetime, timedelta
from starlette.responses import JSONResponse
from sqlalchemy import desc

import json
import urllib.request
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

#IP주소 국가코드가 KR이면 True
def IP(request: Request):
    IP = request.client.host
    key = 'B1gJBJxC7p%2F%2BN9qGjgKEi%2FU6LePtHCPxltLYo7I7%2B2%2FIu1Jei5VYqg%2B8MIwp2BWODMsoOe7hc9th8kW5A4aZew%3D%3D'
    URL = 'http://apis.data.go.kr/B551505/whois/ipas_country_code?serviceKey='+ key + '&query='+ IP +'&answer=json'
    json_page = urllib.request.urlopen(URL)
    json_data = json_page.read().decode("utf-8")
    json_array = json.loads(json_data)
    contrycode = json_array.get("response").get("whois").get("countryCode")
    if contrycode == "KR":
        return True


@app.get("/")
def main():
    return RedirectResponse(url="/docs")


#회원가입
@app.post("/register/{login_id}/{login_pw}/{nickname}/{name}/{email}/{phone}",status_code=200)
async def register(login_id: str, login_pw:str, nickname: str, name: str, email:str, phone: str,request: Request,db:Session = Depends(get_db)):
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
        return {"result":"TRUE"}
    elif is_verified == False or is_exist == False:
        return {"result":"FALSE"}
    else:
        return {"result":"FALSE"}

   


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


# 특정방 찾기
@app.get("/findRoomInfo/{room_name}",status_code=200)
async def find_room(room_name:str,db:Session=Depends(get_db)):    
    q = db.query(models.RoomList.id,
                models.RoomList.created_at,
                models.RoomList.room_name,
                models.RoomList.user_id,
                models.Room_Management.temp, 
                models.Room_Management.humitiy, 
                models.Room_Management.finedust, 
                models.Room_Management.ledcolor). \
            join(models.RoomList, models.RoomList.id == models.Room_Management.room_id). \
            filter_by(room_name=room_name). \
            order_by(models.RoomList.id).all()
    return q


#방 정보 생성 - 하드웨어
@app.post("/addRoomInfo/{room_name}",status_code=200 , response_model=schemas.Room)
def add_room(room_name:str, entrada: schemas.Room, db:Session = Depends(get_db)):
    db_room_id = db.query(models.RoomList.id).filter_by(room_name=room_name)
    new_roomInfo = models.Room_Management.create(db, auto_commit=True, 
                                    room_id = db_room_id,
                                    temp = entrada.temp,
                                    humitiy= entrada.humitiy,
                                    finedust= entrada.finedust,
                                    ledcolor= entrada.ledcolor)
    db.add(new_roomInfo)
    db.commit()

    return new_roomInfo


# id에 해당하는 방 목록
@app.get("/findRoom/{login_id}",status_code=200)
def find_room(login_id:str,request: Request,db:Session=Depends(get_db)):
    db_user_id = db.query(models.User.id).filter_by(login_id=login_id).scalar_subquery()
    room = db.query(models.RoomList.room_name).filter_by(user_id=db_user_id).all()

    return room



# 모든 방에 대한 정보
@app.get("/allRoomInfo",status_code=200)
async def all_room(db:Session=Depends(get_db)):
    q = db.query(models.RoomList.id,
                models.RoomList.created_at,
                models.RoomList.room_name,
                models.RoomList.user_id,
                models.Room_Management.temp, 
                models.Room_Management.humitiy, 
                models.Room_Management.finedust, 
                models.Room_Management.ledcolor). \
            join(models.Room_Management, models.RoomList.id == models.Room_Management.room_id). \
            order_by(models.RoomList.id).all()
    return q

# 방 이름 수정 
@app.put("/update_roomName/{old_room_name}/{new_room_name}",status_code=200)
async def update_room(old_room_name:str, new_room_name:str, db:Session=Depends(get_db)):
    room_name_update=db.query(models.RoomList).filter(models.RoomList.room_name==old_room_name)
    if not room_name_update:
        return {"result":"FALSE"}
    room_name_update.update({'room_name':new_room_name})
    db.commit()
   
    return {"result":"TRUE"}


# 방은 그대로 두고 방에 대한 상세정보 삭제
@app.delete("/delete_room/{room_name}",status_code=200)
async def delete_room(room_name:str, db:Session=Depends(get_db)):
    room_id=db.query(models.RoomList.id).filter_by(room_name=room_name).scalar_subquery()
    id = db.query(models.Room_Management.id).filter_by(room_id=room_id).first()
    room_info_delete = db.query(models.Room_Management).get(id)
    if not room_info_delete:
        return {"result":"FALSE"}
    db.delete(room_info_delete)
    db.commit()
    db.close()

    return {"result":"TRUE"}

# 웹 통계
@app.get("/stat_web/{login_id}/{room_name}/{start}/{amount}",status_code=200)
def stat_info(login_id:str,room_name:str,start:int,amount:int,db:Session=Depends(get_db)):
    db_user_id = db.query(models.User.id).filter_by(login_id=login_id).scalar_subquery()

    q = db.query(models.Room_Management.temp, 
                models.Room_Management.humitiy, 
                models.Room_Management.finedust). \
            join(models.RoomList, models.RoomList.id == models.Room_Management.room_id). \
            filter_by(user_id=db_user_id, room_name = room_name). \
            order_by(desc(models.Room_Management.created_at)). \
            offset(start-1).limit(amount).all()
            
    return q


# 안드로이드


#홈화면
@app.get("/home/{login_id}",response_model=schemas.Room,status_code=200) # 하드웨어에서 현재위치를 받아 그 위치의 가장 최근 정보 전달-> 수정해야 함
def home_info(login_id:str, db:Session=Depends(get_db)):
    db_user_id = db.query(models.User.id).filter_by(login_id=login_id).scalar_subquery()
    db_room_id = db.query(models.RoomList.id).filter_by(user_id=db_user_id,room_name="tt").scalar_subquery()
    room_info = db.query(models.Room_Management).filter_by(room_id=db_room_id).order_by(desc(models.Room_Management.created_at)).first()

    return room_info

#통계 화면
@app.get("/stat/{login_id}/{room_name}/{startdate}/{enddate}",status_code=200)
def stat_info(login_id:str,room_name:str,startdate:str,enddate:str,db:Session=Depends(get_db)):
    db_user_id = db.query(models.User.id).filter_by(login_id=login_id).scalar_subquery()

    q = db.query(models.Room_Management.temp, 
                models.Room_Management.humitiy, 
                models.Room_Management.finedust, 
                ). \
            join(models.RoomList, models.RoomList.id == models.Room_Management.room_id). \
            filter_by(user_id=db_user_id, room_name = room_name). \
            filter(startdate < models.Room_Management.created_at, models.Room_Management.created_at < enddate).all()
            
    return {"result":q}



if __name__  == '__main__':
    uvicorn.run(app="main:app", 
                host="203.250.133.171", #192.168.219.106 203.250.133.171
                port=8000,
                reload=True,
                ssl_keyfile="C:\\Users\\gksek\\capstone\\fastapi\\app\\ssl\\key.pem",
                ssl_certfile="C:\\Users\\gksek\\capstone\\fastapi\\app\\ssl\\cert.pem",
                ) 