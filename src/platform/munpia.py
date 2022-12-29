import datetime

from typing import Final, List
from urllib import parse

from src.exception import WrongPageException

from .novel_platform import Platform
from .result import Result, PlatformType, Episode, Tag

class Munpia(Platform):
  def __init__(self) -> None:
    super().__init__()
    self.SEARCHLINK: Final[str] =  "https://novel.munpia.com/page/novelous/keyword"
    self.RECENTLINK: Final[str] =  "https://novel.munpia.com/page/hd.platinum/group/pl.serial/exclusive/true/view/allend"

  def __searchURL(self, word: str) -> str:
    word = parse.quote(word)
    return f"{self.SEARCHLINK}/{word}/order/search_result"

  def __getEpisodeURL(self, url: str, page: int) -> str:
    return f"{url}/page/{page}"

  async def searchEpisode(self, url: str) -> List[Episode]:
    page = 1
    result = []
    content = None

    # TODO 후일 비동기 적으로 변경할 것
    
    while True:
      try:
        url_page = self.__getEpisodeURL(url, page)
        content = await self._getContentParser(url_page)

        tbody = content.find("table", {"id":"ENTRIES"}).find("tbody")

        for tr in tbody.find_all("tr", {"class":None}):
          idx = int(tr.find("td", {"class":"index"}).text)
          _tc = tr.find("td", {"class":"subject"}).find_all("a")

          comment = 0

          if len(_tc) > 1:
            comment = int(_tc[-1].text.replace("+", ""))
          
          title = _tc[0].text

          date_info = tr.find("td", {"class":"date"}).text

          cur_date = datetime.datetime.now()

          if date_info.find("전") >= 0:
            date = str(cur_date.date())
          else:
            _dinfo = [int(x) for x in date_info.split(".")]
            _dinfo[0] += 2000

            date = datetime.date(*_dinfo)
          
          view, good, word_size = tr.find_all("td", {"class":"number"})

          view = int(view.text.replace(",", "").strip())
          good = int(good.text.replace(",", "").strip())
          word_size = word_size.text.strip()

          result.append(
            Episode(
              idx=idx,
              title=title,
              word_size=str(word_size),
              view=view,
              comment=comment,
              good=good,
              date=str(date),
            )
          )

        page += 1

        pLst = content.find("div", {"class":"pagination"}).find("ul").find_all("li")

        if not page in [int(x.text.strip()) for x in pLst if x.find("a").get("class") == None]:
          break

      except Exception as e:
        raise WrongPageException("파싱에 오류가 발생하였습니다.")

    return result
  
  async def searchRecentLink(self) -> List[str]:
    content = await self._getContentParser(self.RECENTLINK)

    section = content.find("section", {"class":"ns-list"})
    lst = section.find_all("li", {"class":"mi"})

    result = [x.find("a", {"class":"title"})["href"] for x in lst]

    return result

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
    
    try:
      novel_content = content.find("div", {"class":"novel-info"})

      thumbnail = None

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

      description = novel_content.find("p", {"class":"story"}).text

      tag_wrap = novel_content.find("div", {"class":"novel-info-area"})

      tags = [] if tag_wrap == None else [Tag(name=tag.text.strip()) for tag in tag_wrap.find_all("a")]

      is_end = not not (novel_content.find("span", {"class":"xui-finish"}))
      is_plus = not not (novel_content.find("span", {"class":"xui-gold"}))
      
      age_limit = 0

      title = content.find("title").text.split(" « ")[0]

      number_text = novel_content.find_all("dl", {"class":"meta-etc meta"})[1].text
      number_list_1 = [''.join(i for i in x if i.isdigit()) for x in number_text.split("\n")]
      number_list_2 = [int(x) for x in number_list_1 if len(x)]
      
      book, view, good, _ = number_list_2
      
    except Exception as e:
      raise WrongPageException("파싱에 오류가 발생하였습니다.")

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
      author=author,
      description=description,
      tags=tags
    )
