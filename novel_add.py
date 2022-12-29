
from dotenv import load_dotenv

load_dotenv()

import argparse
import asyncio
import platform

if platform.system()=='Windows':
  asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from datetime import datetime
from typing import List

from src import NovelStatistics
from src.db import session, Novel, Tag

from src.platform import Result, Tag as ResultTag

app = NovelStatistics()

def parseResult(item: Result):
  data = item.data
  tags = item.tags
  
  del data["view"]
  del data["good"]
  del data["book"]
  del data["tags"]

  return data, tags

def commitTag(tags: List[ResultTag]):
  tagLst = []
  for tag in tags:
    dbTag = session.query(Tag).filter(Tag.name == tag.name).one_or_none()
    if dbTag != None:
      tagLst.append(dbTag)
    else:
      t = Tag(**tag.data)
      tagLst.append(t)
      session.add(t)
  
  session.commit()

  [session.refresh(t) for t in tagLst]

  return tagLst

def commitDB(item: Result, _id: int = None):
  data, tags = parseResult(item)

  data["tags"] = commitTag(tags)

  if _id == None:
    session.add(Novel(**data))
  else:
    novel = session.query(Novel).filter(Novel.id == _id).one()
    novel.tags = data["tags"]

  session.commit()

async def main():
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

    commitDB(item, _id=_id)

  print("=== 소설 추가 완료 ===")


async def doNow(_input: str):
  item = await app.search(_input)

  if type(item) == list:
    for i in item:
      commitDB(i)
  else:
    commitDB(item)

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
    
    print(f" [x] 소설 크롤링 봇이 실행되었습니다. 이 프로그램의 작동 주기는 [{args.start}]분 입니다.")

    while True:
      loop.run_until_complete(schedule.run_pending())
      sleep(0.1)
