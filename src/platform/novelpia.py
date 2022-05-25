import json

from typing import Final
from urllib import parse

from platform.result.result import PlatformType

from .platform import Platform
from .result import Result

class Novelpia(Platform):
  def __init__(self) -> None:
    super().__init__()
    self.SEARCHLINK: Final[str] =  "https://novelpia.com/proc"
    self.NOVELLINK: Final[str] = "https://novelpia.com/novel"

  def __searchURL(self, word: str) -> str:
    word = parse.quote(word)
    return f"{self.SEARCHLINK}/novelsearch/{word}"

  def __novelURL(self, num: int) -> str:
    return f"{self.NOVELLINK}/{num}"

  # 소설 제목으로 검색
  def searchTitle(self, title: str) -> Result:
    url = self.__searchURL(title)
    content = json.loads(self._getContent(url))

    novel = content["data"]["search_result"][0]["novel_no"]

    return self.searchURL(self.__novelURL(novel))

  # 소설 링크로 검색
  def searchURL(self, url: str) -> Result:
    content = self._getContentParser(url)

    novel_content = content.find("div", {"class":"mobile_hidden s_inv"}).find("div").find("table")
    number_data = novel_content.find_all("tr")[2].find("div").find("font").text

    thumbnail = "https:" + novel_content \
      .find("tr") \
      .find("td") \
      .find("a") \
      .find("img")["src"] \
      .strip()
    title = novel_content \
      .find("tr") \
      .find_all("td")[1] \
      .find("span").text

    number_text = [int(''.join(i for i in x if i.isdigit())) for x in number_data.replace(",", "").replace('\xa0', "").split(" ") if len(x)]
    view, book, good = number_text

    return Result(
      title=title,
      thumbnail=thumbnail,
      view=view,
      book=book,
      good=good,
      type=PlatformType.NOVELPIA,
      link=url
    )
