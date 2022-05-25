import json


from typing import Final, List
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
  def searchTitle(self, title: str) -> List[Result]:
    url = self.__searchURL(title)
    content = json.loads(self._getContent(url))

    novel = content["data"]["search_result"]

    return [self.searchURL(self.__novelURL(novel_num["novel_no"])) for novel_num in novel]

  # 소설 링크로 검색
  def searchURL(self, url: str) -> Result:
    print("노벨피아 - " + url)
    content = self._getContentParser(url)

    novel_content = content.find("div", {"class":"mobile_hidden s_inv"}).find("div").find("table")
    number_data = novel_content.find_all("tr")[2].find("div").find("font").text

    thumbnail_wrap = novel_content \
      .find("tr") \
      .find("td") \
      .find("a")

    thumbnail = None
    if not thumbnail_wrap is None:
      thumbnail = "https:" + thumbnail_wrap \
      .find("img")["src"] \
      .strip()

    title = novel_content \
      .find("tr") \
      .find_all("td")[1] \
      .find("span").text

    number_text = [int(''.join(i for i in x if i.isdigit())) for x in number_data.replace(",", "").replace('\xa0', "").split(" ") if len(x)]
    view, book, good = number_text

    print("노벨피아 완료 - " + url)

    return Result(
      title=title,
      thumbnail=thumbnail,
      view=view,
      book=book,
      good=good,
      type=PlatformType.NOVELPIA,
      link=url
    )
