# pcuCapstoneServer

1. API server를 구축하기 위해 FastAPI를 사용하여 서버를 구축
2. FastAPI를 HTTPS로 띄우기 
3. 사용자와 온도, 습도, 미세먼지 등의 방에 대한 정보를 저장하기 위한 데이터베이스 설계 및 구축

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##1 FastAPI 구축
###프레임워크와  ASGI서버 설치
```c
$ pip install fastapi
$ pip install uvicorn
```

###get, post, delete를 이용하여 웹과 앱에서 접속할 메소드 추가

###회원가입과 로그인
```c
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
```

###방생성과 특정방찾기
```c
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

```
### 데이터베이스 연결
create_engine으 인자값으로 DB URL을 추가하여 DB Host에 DB연결을 생성
![DB연결](https://user-images.githubusercontent.com/69308065/190901977-0b603d62-3898-4a67-8cbf-99052331f770.png)
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##2 HTTPS로 띄우기

```c
choco install mkcert
mkcert -install
mkcert 서버 주소 ::1
```
###발급한 인증서는  "localhost+2.pem"에 있고 키는 "localhost+2-key.pem"에 있다
###파일들을 보기 쉽게 각각 'cert.pem'과 key.pem'으로 바꾸어 저장한다
![ssl](https://user-images.githubusercontent.com/69308065/190902416-cde706f9-e9ee-4727-8147-63090880a5fc.png)

### Uvicron에 파일들의 위치를 알려주고 실행
![main](https://user-images.githubusercontent.com/69308065/190902422-30d9e336-e400-49d6-bd27-db447a79ec00.png)

### 서버가 HTTPS로 잘 띄워지는 것을 확인
![https](https://user-images.githubusercontent.com/69308065/190902574-cedee794-d1ae-4dfe-a406-0cdcef4bbd4d.png)

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##3 데이터베이스 설계
![테이블1](https://user-images.githubusercontent.com/69308065/190901303-4bc9d66b-5dc8-49b1-8a2d-1de9e5483511.png)


 

