from dotenv import load_dotenv

load_dotenv()

import argparse
import asyncio
import platform

if platform.system()=='Windows':
  asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from src import NovelStatic

async def main():
  parser = argparse.ArgumentParser(description="소설 통계 프로그램")

  parser.add_argument("input", help="소설 제목 혹은 링크")

  args = parser.parse_args()

  result = await NovelStatic().search(args.input)

  if result == None: return

  if type(result) == list:
    for i in result: print(i)
  else:
    print(result)
  
if __name__ == '__main__':
  asyncio.run(main())