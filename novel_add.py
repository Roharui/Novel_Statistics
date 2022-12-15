
from dotenv import load_dotenv

load_dotenv()

import argparse
import asyncio
import platform

if platform.system()=='Windows':
  asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from datetime import datetime

from src import NovelStatic
from db import session, Novel

from src.platform import Result

app = NovelStatic()

def parseResult(item: Result):
  data = item.data
  
  del data["view"]
  del data["good"]
  del data["book"]

  return data

def insertDB(item: Result):
  data = parseResult(item)
  session.add(Novel(**data))

def updateDB(_id: int, item: Result):
  data = parseResult(item)
  session.query(Novel).filter(Novel.id == _id).update(data)

async def main():
  print(f" [x] 소설 크롤링 봇이 실행되었습니다. 이 프로그램의 작동 주기는 [{args.start}]분 입니다.")
  result = await app.searchRecentLink()

  print(f"=== 소설 추가 시작 ===")
  print(f"{datetime.now()}")
  for i in result:

    print(f"{i} - 검색 시작")

    _id = session.query(Novel.id).filter(Novel.link == i).scalar()
    item = await app.search(i)

    if item == None:
      print(f"{i} - 생략됨")
      continue

    if _id == None:
      print(f"{i} - DB 주입중")
      insertDB(item)

    else:
      print(f"{i} - DB 수정중")
      updateDB(_id, item)

  print("=== 소설 추가 완료 ===")

  session.commit()


async def doNow(_input: str):
  item = await app.search(_input)

  if type(item) == list:
    for i in item:
      insertDB(i)
  else:
    insertDB(item)

  session.commit()
  
if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="소설 크롤링 봇")

  parser.add_argument("--input", required=False, help="소설 제목 혹은 링크")
  parser.add_argument("--now", required=False, default=False, help="바로 시작", action='store_true')
  parser.add_argument("--start", type=int, required=False, default="5", help="프로그램 시작 시간 (분)")

  args = parser.parse_args()

  if args.input:
    asyncio.run(doNow(args.input))
  elif args.now:
    asyncio.run(main())
  else:
    import aioschedule as schedule
    from time import sleep

    schedule.every(args.start).minutes.do(main)

    loop = asyncio.get_event_loop()

    while True:
      loop.run_until_complete(schedule.run_pending())
      sleep(0.1)
