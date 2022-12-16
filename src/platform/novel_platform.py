'''
소설 검색의 베이스

통계기능은 따로 작업이 필요할 것.

TODO 19금 검색 불가 문제가 존재
'''

from typing import Final, List
from bs4 import BeautifulSoup
from aiohttp import ClientSession

from .result import Result, Episode

GET_HEADER: Final[dict] = {
  'User-Agent': ('Mozilla/5.0 (Windows NT 10.0;Win64; x64)\
  AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98\
  Safari/537.36')
}

POST_HEADER: Final[dict] = {
  "Content-Type": "application/json",
}

POST_HEADER_FORM: Final[dict] = {
  "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
}

class Platform:

  def __init__(self) -> None:
    self.SEARCHLINK = None

  # 소설 검색 기능
  async def _getContent(self, link: str) -> bytes:
    result = None

    async with ClientSession() as session:
      async with session.get(link, headers=GET_HEADER) as response:
        result = await response.text()
    
    return result

  async def _postContent(self, link: str, data: str, json: bool = True) -> bytes:
    result = None
    header = POST_HEADER if json else POST_HEADER_FORM

    async with ClientSession() as session:
      async with session.post(link, data=data, headers=header) as response:
        result = await response.text()
    
    return result

  async def _getContentParser(self, link: str) -> BeautifulSoup:
    return BeautifulSoup(await self._getContent(link), "html.parser")

  async def _postContentParser(self, link: str, data: str, json: bool = True) -> BeautifulSoup:
    return BeautifulSoup(await self._postContent(link, data, json), "html.parser")

  # 최근 소설 검색
  def searchEpisode(self, link: str) -> List[Episode]:
    return [Episode()]

  # 최근 소설 검색
  def searchRecentLink(self) -> List[str]:
    return ["TEST"]

  # 소설 제목으로 검색
  def searchTitle(self, title: str) -> List[Result]:
    return [Result()]

  # 소설 링크로 검색
  def searchURL(self, url: str) -> Result:
    return Result()