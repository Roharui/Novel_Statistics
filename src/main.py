import argparse
import asyncio

from typing import Dict, List, Union
from urllib.parse import urlparse
from validators import url

from .exception import WrongLinkException
from .novel_platform import Result, Novelpia, Munpia, Kakaopage, Platform

from itertools import chain

import sys

py_ver = int(f"{sys.version_info.major}{sys.version_info.minor}")
if py_ver > 37 and sys.platform.startswith('win'):
  asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

PLATFORM: Dict[str, Platform] = {
  "novelpia.com" : Novelpia(),
  "novel.munpia.com": Munpia(),
  "page.kakao.com": Kakaopage()
}

class NovelStatic:
  def __init__(self, only_link: bool = False) -> None:
    self.only_link = only_link

  async def search(self, __input: str) -> Union[Result, List[Result]]:

    self.title = None
    self.url = None

    if url(__input):
      self.url = __input
    else:
      self.title = __input

    # 이름 일 경우
    if self.title:
      if self.only_link:
        return None
      coroutine = await asyncio.gather(*[engin.searchTitle(self.title) for engin in PLATFORM.values()])
      result = await asyncio.gather(*chain(*coroutine))
      return result
    # 링크일 경우
    else:
      host = urlparse(self.url).hostname

      if not host in PLATFORM.keys():
        raise WrongLinkException()
      
      engin: Platform = PLATFORM[host]

      return await engin.searchURL(self.url)

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