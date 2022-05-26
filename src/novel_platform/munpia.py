import json


from typing import Final
from urllib import parse

from novel_platform.result.result import PlatformType

from .novel_platform import Platform
from .result import Result

class Munpia(Platform):
  def __init__(self) -> None:
    super().__init__()
    self.SEARCHLINK: Final[str] =  "https://novel.munpia.com/page/novelous/keyword"

  def __searchURL(self, word: str) -> str:
    word = parse.quote(word)
    return f"{self.SEARCHLINK}/{word}/order/search_result"

  # 소설 제목으로 검색
  async def searchTitle(self, title: str) -> Result:
    url = self.__searchURL(title)
    content = await self._getContentParser(url)

    return [
      self.searchURL(novel["href"])
      for novel in content.find_all("a", {"class":"title col-xs-6"})
    ]

  # 소설 링크로 검색
  async def searchURL(self, url: str) -> Result:
    content = await self._getContentParser(url)
    novel_content = content.find("div", {"class":"novel-info"})

    thumbnail = "https:" + novel_content \
      .find("div", {"class": "dt cover-box"}) \
      .find("img")["src"] \
      .strip()
    title = content.find("title").text.split(" « ")[0]

    number_text = novel_content.find_all("dl", {"class":"meta-etc meta"})[1].text
    number_list_1 = [''.join(i for i in x if i.isdigit()) for x in number_text.split("\n")]
    number_list_2 = [int(x) for x in number_list_1 if len(x)]
    
    book, view, good, _ = number_list_2

    return Result(
      title=title,
      thumbnail=thumbnail,
      view=view,
      book=book,
      good=good,
      type=PlatformType.MUNPIA,
      link=url
    )
