
import argparse
import asyncio

from src import NovelStatic

async def main():
  parser = argparse.ArgumentParser(description="소설 통계 프로그램")

  parser.add_argument("input", help="소설 제목 혹은 링크")

  args = parser.parse_args()

  result = await NovelStatic().search(args.input)

  if type(result) == list:
    for i in result: print(i)
  else:
    print(result)
  
if __name__ == '__main__':
  asyncio.run(main())