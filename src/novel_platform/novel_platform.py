'''
소설 검색의 베이스

통계기능은 따로 작업이 필요할 것.
'''

from typing import Final
from bs4 import BeautifulSoup
from aiohttp import ClientSession

from .result import Result

GET_HEADER: Final[dict] = {
  'User-Agent': ('Mozilla/5.0 (Windows NT 10.0;Win64; x64)\
  AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98\
  Safari/537.36')
}

POST_HEADER: Final[dict] = {
  "Content-Type": "application/json",
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

  async def _postContent(self, link: str, data: str) -> bytes:
    result = None

    async with ClientSession() as session:
      async with session.post(link, data=data, headers=POST_HEADER) as response:
        result = await response.text()
    
    return result

  async def _getContentParser(self, link: str) -> BeautifulSoup:
    return BeautifulSoup(await self._getContent(link), "html.parser")

  # 소설 제목으로 검색
  def searchTitle(self, title: str) -> Result:
    return Result()

  # 소설 링크로 검색
  def searchURL(self, url: str) -> Result:
    return Result()