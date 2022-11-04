
from enum import unique
from operator import index
from pymysql import Timestamp
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, func, DateTime, Enum
from sqlalchemy.orm import relationship
from db import Base

from tkinter import CASCADE
from sqlalchemy.orm import Session

class BaseMixin:
    id = Column(Integer, primary_key=True, index=True, unique=True)
    created_at = Column(DateTime, nullable=False, default=func.utc_timestamp())
    updated_at = Column(DateTime, nullable=False, default=func.utc_timestamp(), onupdate=func.utc_timestamp())

    def __init__(self):
        self._q = None
        self._session = None
        self.served = None

    def all_columns(self):
        return [c for c in self.__table__.columns if c.primary_key is False and c.name != "created_at"]

    def __hash__(self):
        return hash(self.id)

    @classmethod
    def create(cls, db: Session, auto_commit=False, **kwargs):
        """
        테이블 데이터 적재 전용 함수
        :param session:
        :param auto_commit: 자동 커밋 여부
        :param kwargs: 적재 할 데이터
        :return:
        """
        obj = cls()
        for col in obj.all_columns():
            col_name = col.name
            if col_name in kwargs:
                setattr(obj, col_name, kwargs.get(col_name))
        db.add(obj)
        db.flush()
        if auto_commit:
            db.commit()
        return obj

# 사용자 정보 테이블
class User(Base,BaseMixin):
    __tablename__ = 'users'
    nickname= Column(String(length=255),unique=True,index=True) # 닉네임
    login_id= Column(String(length=255),unique=True,index=True) #아이디
    login_pw= Column(String(length=255)) # 비밀번호
    name= Column(String(length=255)) # 이름
    email= Column(String(length=255),index=True,unique=True) # 이메일
    phone= Column(String(length=255),unique=True, index=True) # 전화번호

    token = relationship(
        "Token",
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )


    list = relationship(
        "RoomList",
        back_populates="users",
        cascade="all, delete",
        passive_deletes=True,
    )

class Token(Base, BaseMixin):
    __tablename__ = 'token'

    user_id = Column(Integer,ForeignKey("users.id",ondelete="CASCADE"))
    access_token = Column(String,unique=True,index=True)
    
    user = relationship("User",back_populates="token")
    

# 방 목록 테이블
class RoomList(Base,BaseMixin):
    __tablename__ = 'room_list'

    user_id= Column(Integer,ForeignKey("users.id",ondelete="CASCADE"))
    room_name= Column(String(length=255),index=True,unique=True)
   
    users = relationship("User",back_populates="list")
    room = relationship(
        "Room_Management",
        back_populates="room_list",
        cascade="all, delete",
        passive_deletes=True,
    )
    move = relationship(
        "Move",
        back_populates="room_list",
        cascade="all, delete",
        passive_deletes=True,
    )
    

#방 관리 테이블
class Room_Management(Base,BaseMixin):
    __tablename__ = 'room'

    room_id= Column(Integer,ForeignKey("room_list.id",ondelete="CASCADE"))
    temp= Column(Integer, index=True)
    humitiy= Column(Integer, index=True)
    finedust= Column(Integer, index=True)
    ledcolor= Column(String(length=255) ,index=True)

    room_list = relationship("RoomList",back_populates="room")

# 이동 테이블
class Move(Base, BaseMixin):
    __tablename__ = 'move'

    room_id = Column(Integer,ForeignKey("room_list.id",ondelete="CASCADE"))
    move_selected = Column(String(length=255), Enum("auto","time","random"),index=True)
    move_set = Column(String(length=255),nullable=True)

    room_list= relationship("RoomList",back_populates="move")



     




