from pydantic import BaseModel, EmailStr

class User(BaseModel):
    nickname: str
    login_id: str
    login_pw: str
    name: str
    email: EmailStr
    phone: str

    class Config:
        orm_mode = True

class Room_Info(BaseModel):
    room_id: int
    temp: int
    humitiy= int
    finedust= int
    ledcolor= str

    class Config:
        orm_mode = True


class RoomList(BaseModel):
    room_name:str
    user_id:int

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    login_id: str
    login_pw: str
    
    class Config:
        orm_mode = True


class Token(BaseModel):
    Authorizaion: str= None
    
    class Config:
        orm_mode = True

class UserToken(BaseModel):
    id: int  
    nickname: str
    login_id: str
    #login_pw: str
    name: str
    email: EmailStr
    phone: str

    class Config:
        orm_mode = True