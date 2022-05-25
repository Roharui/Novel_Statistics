import json

from typing import Final
from urllib import parse

from platform.result.result import PlatformType

from .platform import Platform
from .result import Result

class Munpia(Platform):
  def __init__(self) -> None:
    super().__init__()
    self.SEARCHLINK: Final[str] =  "https://novel.munpia.com/page/novelous/keyword"

  def __searchURL(self, word: str) -> str:
    word = parse.quote(word)
    return f"{self.SEARCHLINK}/{word}/order/search_result"

  # 소설 제목으로 검색
  def searchTitle(self, title: str) -> Result:
    url = self.__searchURL(title)
    content = self._getContentParser(url)

    return self.searchURL(content.find("a", {"class":"title"})["href"])

  # 소설 링크로 검색
  def searchURL(self, url: str) -> Result:
    content = self._getContentParser(url)
    novel_content = content.find("div", {"class":"novel-info"})

    thumbnail = "https:" + novel_content \
      .find("div", {"class": "dt cover-box"}) \
      .find("img")["src"] \
      .strip()
    title = novel_content \
      .find("div", {"class":"dd detail-box"}) \
      .find("h2")
    title.find("span").decompose()
    title = title.text.strip()

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
      type=PlatformType.MUNPIA
    )
