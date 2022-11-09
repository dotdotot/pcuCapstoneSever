from fastapi import APIRouter
from requests import Session
from fastapi.params import Depends
from sqlalchemy import desc
from db import get_db

import models, schemas

router = APIRouter(prefix="/androidMethod",tags=["androidMethod"])

@router.get("/test")
def test():
    return {"message":"아아"}

#홈화면
@router.get("/home/{login_id}",response_model=schemas.Room,status_code=200) # 하드웨어에서 현재위치를 받아 그 위치의 가장 최근 정보 전달-> 수정해야 함
def home_info(login_id:str, db:Session=Depends(get_db)):
    db_user_id = db.query(models.User.id).filter_by(login_id=login_id).scalar_subquery()
    db_room_id = db.query(models.RoomList.id).filter_by(user_id=db_user_id,room_name="eee").scalar_subquery()
    room_info = db.query(models.Room_Management).filter_by(room_id=db_room_id).order_by(desc(models.Room_Management.created_at)).first()

    return room_info

#통계 화면
@router.get("/stat/{login_id}/{room_name}/{startdate}/{enddate}",status_code=200)
def stat_info(login_id:str,room_name:str,startdate:str,enddate:str,db:Session=Depends(get_db)):
    db_user_id = db.query(models.User.id).filter_by(login_id=login_id).scalar_subquery()

    q = db.query(models.Room_Management.temp, 
                models.Room_Management.humidity, 
                models.Room_Management.finedust, 
                ). \
            join(models.RoomList, models.RoomList.id == models.Room_Management.room_id). \
            filter_by(user_id=db_user_id, room_name = room_name). \
            filter(startdate < models.Room_Management.created_at, models.Room_Management.created_at < enddate).all()
            
    return {"result":q}


# 이동화면
@router.post("/move/{login_id}/{move_select}/{move_set}/{room_name}",status_code=200)
async def register(login_id: str, move_select:str, move_set:str, room_name: str,db:Session = Depends(get_db)):
    id_exist = db.query(models.User.login_id).filter_by(login_id=login_id).first()
    room_exist = db.query(models.RoomList.room_name).filter_by(room_name=room_name).first()
    db_room_id = db.query(models.RoomList.id).filter_by(room_name=room_name)
    
    if not id_exist or not room_exist:
        return {"result":"FALSE"}
        
    else:
        models.Move.create(db,auto_commit=True,room_id =db_room_id,move_select=move_select,move_set=move_set)
        return {"result":"TRUE"}
