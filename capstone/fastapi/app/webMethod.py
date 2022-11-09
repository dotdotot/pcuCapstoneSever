from fastapi import APIRouter
from requests import Session
from fastapi.params import Depends
from sqlalchemy import desc

import models, schemas

from db import get_db


router = APIRouter(prefix="/webMethod",tags=["webMethod"])

# 회원 정보를 보여주기 위한 기능
@router.get("/userInfo/{login_id}",status_code=200)
async def user_info(login_id:str,db:Session=Depends(get_db)):
    q = db.query(models.User.id,
                models.User.created_at,
                models.User.name,
                models.User.login_id,
                models.User.nickname,
                models.User.email,). \
            filter_by(login_id=login_id).all()

    return q

# 특정방 찾기
@router.get("/findRoomInfo/{room_name}",status_code=200)
async def find_room(room_name:str,db:Session=Depends(get_db)):    
    q = db.query(models.RoomList.id,
                models.RoomList.created_at,
                models.RoomList.room_name,
                models.RoomList.user_id,
                models.Room_Management.temp, 
                models.Room_Management.humidity, 
                models.Room_Management.finedust, 
                models.Room_Management.ledcolor). \
            join(models.RoomList, models.RoomList.id == models.Room_Management.room_id). \
            filter_by(room_name=room_name). \
            order_by(models.RoomList.id).all()
    return q


#방 정보 생성 - 하드웨어
@router.post("/addRoomInfo/{room_name}",status_code=200 , response_model=schemas.Room)
def add_room(room_name:str, entrada: schemas.Room, db:Session = Depends(get_db)):
    db_room_id = db.query(models.RoomList.id).filter_by(room_name=room_name)
    new_roomInfo = models.Room_Management.create(db, auto_commit=True, 
                                    room_id = db_room_id,
                                    temp = entrada.temp,
                                    humidity= entrada.humidity,
                                    finedust= entrada.finedust,
                                    ledcolor= entrada.ledcolor)
    db.add(new_roomInfo)
    db.commit()

    return new_roomInfo


# id에 해당하는 방 목록
@router.get("/findRoom/{login_id}",status_code=200)
def find_room(login_id:str, db:Session=Depends(get_db)):
    db_user_id = db.query(models.User.id).filter_by(login_id=login_id).scalar_subquery()
    room = db.query(models.RoomList.room_name).filter_by(user_id=db_user_id).all()

    return room



# 모든 방에 대한 정보
@router.get("/allRoomInfo",status_code=200)
async def all_room(db:Session=Depends(get_db)):
    q = db.query(models.RoomList.id, 
                models.RoomList.created_at, 
                models.RoomList.room_name, 
                models.RoomList.user_id, 
                models.Room_Management.temp, 
                models.Room_Management.humidity, 
                models.Room_Management.finedust, 
                models.Room_Management.ledcolor). \
            join(models.Room_Management, models.RoomList.id == models.Room_Management.room_id). \
            order_by(models.RoomList.id).all()
    return q

# 방 이름 수정 
@router.put("/update_roomName/{old_room_name}/{new_room_name}",status_code=200)
async def update_room(old_room_name:str, new_room_name:str, db:Session=Depends(get_db)):
    room_exist = db.query(models.RoomList.room_name).filter_by(room_name=old_room_name).first()
    
    if room_exist:
        db.query(models.RoomList).filter(models.RoomList.room_name==old_room_name). \
                        update({'room_name':new_room_name})
        return {"result":"TRUE"}
    db.commit()
   
    return {"result":"FALSE"}


# 방은 그대로 두고 방에 대한 상세정보 삭제
@router.delete("/delete_room/{room_name}",status_code=200)
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
@router.get("/stat_web/{room_name}/{start}/{amount}",status_code=200)
def stat_info(room_name:str,start:int,amount:int,db:Session=Depends(get_db)):
    q = db.query(models.RoomList.id, 
                models.RoomList.room_name, 
                models.RoomList.user_id,
                models.Room_Management.created_at,   
                models.Room_Management.temp, 
                models.Room_Management.humidity, 
                models.Room_Management.finedust, 
                models.Room_Management.ledcolor). \
            join(models.RoomList, models.RoomList.id == models.Room_Management.room_id). \
            filter_by(room_name = room_name). \
            order_by(desc(models.Room_Management.created_at)). \
            offset(start-1).limit(amount).all()
            
    return q


# 날짜가 일부라도 겹치는 데이터들만 시작 숫자 부터 보여줄 데이터 양 까지 리턴
@router.get("/findDate/{searchText}/{room_name}/{start}/{amount}",status_code=200)
def stat_info(searchText:str,room_name:str,start:int,amount:int,db:Session=Depends(get_db)):
    Date = models.Room_Management.created_at.contains(searchText,autoescape=True)
    q = db.query(models.RoomList.id, 
                models.RoomList.room_name, 
                models.RoomList.user_id,
                models.Room_Management.created_at,  
                models.Room_Management.temp, 
                models.Room_Management.humidity, 
                models.Room_Management.finedust, 
                models.Room_Management.ledcolor). \
            join(models.RoomList, models.RoomList.id == models.Room_Management.room_id). \
            filter_by(room_name = room_name). \
            where(Date). \
            order_by(desc(models.Room_Management.created_at)). \
            offset(start-1).limit(amount).all()
            
    return q

# 미세먼지 특정 값만을 리턴해주는 역할
@router.get("/findFinedust/{searchText}/{room_name}/{start}/{amount}",status_code=200)
def stat_info(searchText:str,room_name:str,start:int,amount:int,db:Session=Depends(get_db)):
    q = db.query(models.RoomList.id, 
                models.RoomList.room_name, 
                models.RoomList.user_id, 
                models.Room_Management.created_at,  
                models.Room_Management.temp, 
                models.Room_Management.humidity, 
                models.Room_Management.finedust, 
                models.Room_Management.ledcolor). \
            join(models.RoomList, models.RoomList.id == models.Room_Management.room_id). \
            filter_by(room_name = room_name). \
            order_by(desc(models.Room_Management.created_at)). \
            filter(models.Room_Management.finedust == searchText). \
            offset(start-1).limit(amount).all()
            
    return q

# 특정 온도를 포함하는 데이터만 리턴해 주는 역할
@router.get("/findTemp/{searchText}/{room_name}/{start}/{amount}",status_code=200)
def stat_info(searchText:str,room_name:str,start:int,amount:int,db:Session=Depends(get_db)):
    q = db.query(models.RoomList.id, 
                models.RoomList.room_name, 
                models.RoomList.user_id, 
                models.Room_Management.created_at,  
                models.Room_Management.temp, 
                models.Room_Management.humidity, 
                models.Room_Management.finedust, 
                models.Room_Management.ledcolor). \
            join(models.RoomList, models.RoomList.id == models.Room_Management.room_id). \
            filter_by(room_name = room_name). \
            order_by(desc(models.Room_Management.created_at)). \
            filter(models.Room_Management.temp == searchText). \
            offset(start-1).limit(amount).all()
            
    return q

# 특정 습도값만 포함하는 데이터만 리턴해 주는 역할
@router.get("/findHumidity/{searchText}/{room_name}/{start}/{amount}",status_code=200)
def stat_info(searchText:str,room_name:str,start:int,amount:int,db:Session=Depends(get_db)):
    q = db.query(models.RoomList.id, 
                models.RoomList.room_name, 
                models.RoomList.user_id, 
                models.Room_Management.created_at,  
                models.Room_Management.temp, 
                models.Room_Management.humidity, 
                models.Room_Management.finedust, 
                models.Room_Management.ledcolor). \
            join(models.RoomList, models.RoomList.id == models.Room_Management.room_id). \
            filter_by(room_name = room_name). \
            order_by(desc(models.Room_Management.created_at)). \
            filter(models.Room_Management.humidity == searchText). \
            offset(start-1).limit(amount).all()
            
    return q