import json


from typing import Final
from urllib import parse

from src.exception.wrong_page_exception import WrongPageException

from .novel_platform import Platform
from .result import Result, PlatformType

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

    thumbnail = None

    try:
      thumbnail = "https:" + novel_content \
        .find("div", {"class": "dt cover-box"}) \
        .find("img")["src"] \
        .strip()

      author = (
          novel_content.find("dl", {"class":"meta-author meta"}) \
          .find("dd") \
          .find("a")
          or
          novel_content.find("dl", {"class":"meta-author meta"}) \
          .find("dd") \
        ).text.strip()

      is_end = not not (novel_content.find("span", {"class":"xui-finish"}))
      is_plus = not not (novel_content.find("span", {"class":"xui-gold"}))
      
      age_limit = 0

      title = content.find("title").text.split(" « ")[0]

      number_text = novel_content.find_all("dl", {"class":"meta-etc meta"})[1].text
      number_list_1 = [''.join(i for i in x if i.isdigit()) for x in number_text.split("\n")]
      number_list_2 = [int(x) for x in number_list_1 if len(x)]
      
      book, view, good, _ = number_list_2
      
    except AttributeError as e:
      raise WrongPageException

    return Result(
      title=title,
      thumbnail=thumbnail,
      view=view,
      book=book,
      good=good,
      type=PlatformType.MUNPIA,
      link=url,
      is_end=is_end,
      is_plus=is_plus,
      age_limit=age_limit,
      author=author
    )
