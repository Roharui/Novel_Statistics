import asyncio

from typing import Dict, List, Union
from urllib.parse import urlparse
from validators import url

from src.exception import WrongLinkException
from src.novel_platform import Result, Novelpia, Munpia, Kakaopage, Platform

from itertools import chain

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

