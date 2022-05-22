import json

from typing import Final

from .platform import Platform
from .result import Result

class Novelpia(Platform):
  def __init__(self) -> None:
    super().__init__()
    self.SEARCHLINK: Final[str] =  "https://novelpia.com/proc/novelsearch_v2"

  def __searchURL(self, word: str) -> str:
    return f"{self.SEARCHLINK}?search_text={word}"

  # 소설 제목으로 검색
  def searchTitle(self, title: str) -> Result:
    url = self.__searchURL(title)
    content = json.loads(self._getContent(url))

    print(content)

    return Result()

  # 소설 링크로 검색
  def searchURL(self, url: str) -> Result:
    content = json.loads(self._getContent(url))

    print(content)
    return Result()
