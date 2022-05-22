'''
소설 검색의 베이스

통계기능은 따로 작업이 필요할 것.
'''

from typing import Final
from requests import get, exceptions

from urllib import parse
from .result import Result

HEADER: Final[dict] = {
  'User-Agent': ('Mozilla/5.0 (Windows NT 10.0;Win64; x64)\
  AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98\
  Safari/537.36')
}

class Platform:

  def __init__(self) -> None:
    self.SEARCHLINK = None

  # 소설 검색 기능
  def _getContent(self, link: str) -> bytes:
    result = None

    try:
      result = get(link, headers=HEADER)
    except exceptions.Timeout as errd:
      print("제한 시간 초과 : ", errd)
    
    except exceptions.ConnectionError as errc:
      print("연결 오류 : ", errc)
        
    except exceptions.HTTPError as errb:
      print("Http 오류 : ", errb)

    except exceptions.RequestException as erra:
      print("알수 없는 오류 : ", erra)

    return result.content

  # 소설 제목으로 검색
  def searchTitle(self, title: str) -> Result:
    return Result()

  # 소설 링크로 검색
  def searchURL(self, url: str) -> Result:
    return Result()