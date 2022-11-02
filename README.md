# pcuCapstoneServer

1. API server를 구축하기 위해 FastAPI를 사용하여 서버를 구축
2. FastAPI를 HTTPS로 띄우기 
3. 사용자와 온도, 습도, 미세먼지 등의 방에 대한 정보를 저장하기 위한 
4. 데이터베이스 설계 및 구축
5. 해외IP차단(openAPI 사용)
-------------------------------------------------------------------------------------------------
## FastAPI 구축
### 프레임워크와  ASGI서버 설치
```c
$ pip install fastapi
$ pip install uvicorn
```

## WEB

* register(post)
>사용자에게 login_id, login_pw, nickname, name, email, phone을 json header에서 입력받아 db에 저장(login_pw는 암호화)login_id, nickname, name, email이 존재하는지 확인하고 만약 존재한다면 {"result":"FALSE"}메세지 출력 회원가입에 성공하면 {"result":"TRUE"} 출력
```c
@app.post("/register/{login_id}/{login_pw}/{nickname}/{name}/{email}/{phone}",status_code=200)
```


* login(get)
>사용자에게 login_id와 login_pw를 json body로 입력받고 아이디가 존재하는지 확인, 비밀번호를 인코딩하고 동일한지 확인하고 동일하다면 {"result":"TRUE"} 메세지 리턴 
```c
@app.post("/login/",status_code=200,response_model=schemas.Token)
```

* findRoomInfo(get)
>사용자에게 room_name을 json header에서 입력받아 해당 방의 모든 정보를 json body에 감싸서 리턴
```c
@app.get("/findRoom/{room_name}",status_code=200)
```

* findRoom(get)
>사용자에게 login_id를 json header에서 입력받아 해당 아이디의 방 목록을 json body에 감싸 리턴
```c
@app.get("/findRoom/{login_id}",status_code=200)
```

* allRoomInfo(get)
>지금 존재하는 모든 방에 대한 정보를 json body에 감싸 리턴
```c
@app.get("/allRoomInfo",status_code=200)
```

* update_roomName(put)
>사용자에게 old_room_name, new_room_name을 json header에서 입력받음
>방이 존재하지 않다면 {"result":"FALSE"} 메세지 리턴
>방이 존재하면 입력받은 새 방이름으로 업데이트하고 {"result":"TRUE"} 메세지 리턴
```c
@app.put("/update/{old_room_name}/{new_room_name}",status_code=200)
```

* delete_room(delete)
>사용자에게 room_name을 json header로 입력받음
>방이 존재하지 않다면 {"result":"FALSE"} 메세지 리턴
>방이 존재한다면 해당 방의 모든 정보를 삭제 {"result":"TRUE"} 메세지 리턴
```c
@app.delete("/delete_room/{room_name}",status_code=200)
```

* stat_web(get)
>login_id, room_name, start, amount을 json header로 입력받음
>room테이블의 created_at을 내림차순으로 정렬해서 start-1부터 amount개의 데이터 리턴
```c
@app.get("/stat_web/{login_id}/{room_name}/{start}/{amount}",status_code=200)
```

## ANDROID

* register(post) - 웹과 동일
* login(get) - 웹과 동일
* home(get)
>사용자에게 login_id를 json header로 입력받음
>하드웨어에서 현재 위치를 받음 (하드웨어 연결 후 수정)
>입력받은 아이디의 현재 위치의 가장 최근 정보를 리턴(하드웨어 연결 후 수정)
>(수정 필요)
```c
@app.get("/home/{login_id}",response_model=schemas.Room,status_code=200)
```

* stat(get)
>사용자에게 login_id, room_name, startdate, enddate를 json header로 입력받음
>입력받은 아이디의 해당 방의 시작날짜와 종료날짜 사이의 모든 정보를 리턴 
```c
@app.get("/stat/{login_id}/{room_name}/{startdate}/{enddate}",status_code=200)
```

## HARDWARE
* addRoonInfo(post) - 이걸 기반으로 하드웨어 완료되면 작성
>사용자에게 room_name을 json header에서 입력받고 temp, humitiy, finedust, ledcolor을 json body로 입력받아 db에 저장
```c
@app.post("/addRoomInfo/{room_name}",status_code=200 , response_model=schemas.Room)
```
-------------------------------------------------------------------------------------------------
## HTTPS로 띄우기

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

-------------------------------------------------------------------------------------------------
## 데이터베이스 연결
create_engine의 인자값으로 DB URL을 추가하여 DB Host에 DB연결을 생성
![DB연결](https://user-images.githubusercontent.com/69308065/190901977-0b603d62-3898-4a67-8cbf-99052331f770.png)
## 데이터베이스 설계
![테이블1](https://user-images.githubusercontent.com/69308065/190901303-4bc9d66b-5dc8-49b1-8a2d-1de9e5483511.png)

## OpenAPI사용해서 해외IP차단
>WHOIS OpenAPI활용
>요청변수 : servicekey(공공데이터포털에서 받은 인증키), queay(IP 주소 또는 AS 번호), answer(응답형식(XML/JSON) 을 지정(없으면 XML으로 응답))
>응답을 json형태로 받아 파싱하여 사용자 IP의 국가코드를 알아냄
>국가코드가 KR일때만 모든 메서드 접속허용
>(문제점: 고정 IP주소가 아니면 국가코드를 식별할 수 없음, api에 직접 부착하는 방법 알아보는 중)
```c
 URL = 'http://apis.data.go.kr/B551505/whois/ipas_country_code?serviceKey='+ key + '&query='+ IP +'&answer=json'
json_page = urllib.request.urlopen(URL)
json_data = json_page.read().decode("utf-8")
json_array = json.loads(json_data)
contrycode = json_array.get("response").get("whois").get("countryCode")
```

 

