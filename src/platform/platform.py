'''
소설 검색의 베이스

통계기능은 따로 작업이 필요할 것.
'''

from typing import Final
from bs4 import BeautifulSoup
from requests import get, exceptions, post

from .result import Result

GET_HEADER: Final[dict] = {
  'User-Agent': ('Mozilla/5.0 (Windows NT 10.0;Win64; x64)\
  AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98\
  Safari/537.36')
}

POST_HEADER: Final[dict] = {
  "Accept": "application/json",
  "Accept-Encoding": "gzip, deflate, br",
  "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
  "Connection": "keep-alive",
  "Content-Length": "30",
  "Content-Type": "application/x-www-form-urlencoded",
  "Host": "api2-page.kakao.com",
  "Origin": "https://page.kakao.com",
  "Referer": "https://page.kakao.com/",
  "Sec-Fetch-Dest": "empty",
  "Sec-Fetch-Mode": "cors",
  "Sec-Fetch-Site": "same-site",
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36",
  "sec-ch-ua":'" " Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
  "sec-ch-ua-mobile": "?0",
  "sec-ch-ua-platform": '"Windows"'
}

class Platform:

  def __init__(self) -> None:
    self.SEARCHLINK = None

  # 소설 검색 기능
  def _getContent(self, link: str, data: str=None, GET: bool=True) -> bytes:
    result = None

    try:
      if GET:
        result = get(link, headers=GET_HEADER)
      else:
        result = post(link, data=data, headers=POST_HEADER)
    except exceptions.Timeout as errd:
      print("제한 시간 초과 : ", errd)
    
    except exceptions.ConnectionError as errc:
      print("연결 오류 : ", errc)
        
    except exceptions.HTTPError as errb:
      print("Http 오류 : ", errb)

    except exceptions.RequestException as erra:
      print("알수 없는 오류 : ", erra)

    return result.content

  def _getContentParser(self, link: str) -> BeautifulSoup:
    return BeautifulSoup(self._getContent(link), "html.parser")

  # 소설 제목으로 검색
  def searchTitle(self, title: str) -> Result:
    return Result()

  # 소설 링크로 검색
  def searchURL(self, url: str) -> Result:
    return Result()