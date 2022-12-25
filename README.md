# 웹소설 통계정보 크롤링 프로그램

웹소설 통계정보(조회수, 추천 등)를 크롤링하는 프로그램입니다.

## 검색

단순히 검색하여 정보를 표시합니다.

```
python main.py <링크 또는 소설 제목>
```

## 최신 소설 수집

> DB가 필요합니다.

업로드된 소설의 정보를 DB에 등록합니다.

```
# 소설 제목 또는 링크로 수집
python novel_add --input <소설 제목 또는 링크>
# 최신 소설들 바로 수집
python novel_add --now
# 지속적으로 수집
python novel_add --start <수집 간격>
```

## 소설 정보 수집

> DB 및 RabbitMQ가 필요합니다.

등록된 소설의 정보를 수집합니다. 

다수의 컨슈머를 실행시킨 다음 프로듀서를 실행시켜주세요.

**DDos 공격 취급 방지를 위해 30초 간격으로 소설 정보가 등록됩니다.**

```
# 프로듀서
## 바로 시작
python producer.py --now
## 반복 실행
python producer.py --start <시작 시간>
# 컨슈머
python consumer.py
```

## 환경 변수 설정

> .env 파일을 지원합니다.

postgreSQL로 개발되었으니 되도록이면 해당 DB를 사용해주세요.

```
DB_URL=<DB URL>
MQ_URL=<RabbitMQ URL>
MQ_QUEUE=<queue 이름>

LOG=<에러 로그 출력 방식 [PRINT, FILE, DISCORD]>
FILE_NAME=<에러 로그 출력 파일 이름 (LOG가 FILE일때만 유효합니다)>

WEBHOOK=<DISCORD WEBHOOK>
```

## 플랫폼

> 카카오페이지의 경우 좋아요가 없습니다.

- 노벨피아
- 문피아
- *카카오페이지* (검색만 가능합니다)

## 주의사항

해당 프로그램을 사적으로 사용하는 것 이외의 용도로 사용하지 말아주세요.

해당 프로그램을 사용하므로써 발생하는 모든 불이익은 개발자가 책임지지 않습니다.