
from dotenv import load_dotenv

load_dotenv()

import argparse
import asyncio
import platform

if platform.system()=='Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from src import NovelStatic
from db import session, Novel

from src.novel_platform.result import Result


def insertDB(item: Result):
  data = item.data
  del data["view"]
  del data["good"]
  del data["book"]
  novel = Novel(**data)
  session.add(novel)

async def main():
  parser = argparse.ArgumentParser(description="소설 통계 프로그램")

  parser.add_argument("input", help="소설 제목 혹은 링크")

  args = parser.parse_args()

  result = await NovelStatic().search(args.input)

  if type(result) == list:
    for i in result:
      insertDB(i)
  else:
    insertDB(result)

  session.commit()
  
if __name__ == '__main__':
  asyncio.run(main())