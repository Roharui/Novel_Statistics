import json


from typing import Final, List
from urllib import parse

from src.exception.wrong_page_exception import WrongPageException


from .novel_platform import Platform
from .result import Result, PlatformType

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
  async def searchTitle(self, title: str) -> List[Result]:
    url = self.__searchURL(title)
    content = json.loads(await self._getContent(url))

    novel = content["data"]["search_result"]

    novel_url = [self.__novelURL(novel_num["novel_no"]) for novel_num in novel]

    return [self.searchURL(url) for url in novel_url]

  # 소설 링크로 검색
  async def searchURL(self, url: str) -> Result:
    content = await self._getContentParser(url)

    novel_content = None
    number_data = None

    try:
      novel_content = content.find("div", {"class":"mobile_hidden s_inv"}).find("div").find("table")
      number_data = novel_content.find_all("tr")[2].find("div").find("font").text
    except AttributeError as e:
      raise WrongPageException

    thumbnail_wrap = novel_content \
      .find("tr") \
      .find("td") \
      .find("a") \
      or \
      novel_content \
      .find("tr") \
      .find("td")

    thumbnail = None
    if not thumbnail_wrap is None:
      thumbnail = "https:" + thumbnail_wrap \
      .find("img")["src"] \
      .strip()

      thumbnail = None if thumbnail == "https://image.novelpia.com" else thumbnail

    is_end = not not (novel_content.find("span", {"class" : "b_comp"}))
    is_plus = not not (novel_content.find("span", {"class" : "b_plus"}))

    age_limit = 19 if novel_content.find("span", {"class" : "b_19"}) \
      else 15 if novel_content.find("span", {"class" : "b_15"}) else 0

    title = novel_content \
      .find("tr") \
      .find_all("td")[1] \
      .find("span").text

    author = novel_content \
      .find("tr") \
      .find_all("td")[1] \
      .find_all("font")[1] \
      .find("a").text

    number_text = [int(''.join(i for i in x if i.isdigit())) for x in number_data.replace(",", "").replace('\xa0', "").split(" ") if len(x)]
    view, book, good = number_text

    return Result(
      title=title,
      thumbnail=thumbnail,
      view=view,
      book=book,
      good=good,
      type=PlatformType.NOVELPIA,
      link=url,
      is_end=is_end,
      is_plus=is_plus,
      age_limit=age_limit,
      author=author
    )
