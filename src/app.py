import asyncio

from typing import Dict, List, Union
from urllib.parse import urlparse
from validators import url

from src.exception.wrong_page_exception import WrongPageException
from src.platform import Result, Novelpia, Munpia, Kakaopage, Platform

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
        return []
      try:
        coroutine = await asyncio.gather(*[engin.searchTitle(self.title) for engin in PLATFORM.values()])
        result = await asyncio.gather(*chain(*coroutine))
        return result
      except WrongPageException:
        print("잘못된 페이지입니다.")
        return []
    # 링크일 경우
    else:
      host = urlparse(self.url).hostname

      if not host in PLATFORM.keys():
        print("잘못된 링크입니다.")
        return None
      
      engin: Platform = PLATFORM[host]

      try:
        return await engin.searchURL(self.url)
      except WrongPageException:
        print("잘못된 페이지입니다.")
        return None
    

  async def searchRecentLink(self):
    # 현재로써는 노벨피아만 작동 시킴, 후일 문피아와 카카오페이지도 추가할것.
    plst = [PLATFORM["novelpia.com"], PLATFORM["novel.munpia.com"]]
    coroutine = await asyncio.gather(*[engin.searchRecentLink() for engin in plst])
    return list(chain(*coroutine))

  async def searchEpisode(self, _url: str):
    if url(_url):
      host = urlparse(self.url).hostname

      if not host in PLATFORM.keys():
        print(f"[{_url}] - 잘못된 링크입니다.")
        return []
      
      engin: Platform = PLATFORM[host]

      return await engin.searchEpisode(_url)
    else:
      print(f"[{_url}] - 잘못된 링크입니다.")
      return []