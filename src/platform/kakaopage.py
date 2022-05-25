import json

from typing import Final
from urllib import parse

from platform.result.result import PlatformType

from .platform import Platform
from .result import Result

class Kakaopage(Platform):
  def __init__(self) -> None:
    super().__init__()
    self.SEARCHLINK: Final[str] =  "https://api2-page.kakao.com/api/v5/store/search"

  # 소설 제목으로 검색
  def searchTitle(self, title: str) -> Result:
    word = f"word={parse.quote(title)}"
    content = json.loads(self._getContent(self.SEARCHLINK, data=word, GET=False))

    novel_content = content["results"][2]["items"][0]

    title = novel_content["title"]
    thumbnail = f"https://dn-img-page.kakao.com/download/resource?kid={novel_content['image_url']}&filename=th1"

    view = novel_content["read_count"]
    book = novel_content["page"]
    good = None

    link = f"https://page.kakao.com/home?seriesId={novel_content['id']}"

    return Result(
      title=title,
      thumbnail=thumbnail,
      view=view,
      book=book,
      good=good,
      type=PlatformType.KAKAOPAGE,
      link=link
    )


  # 소설 링크로 검색
  def searchURL(self, url: str) -> Result:
    content = self._getContentParser(url)

    title = content.find("h2", {"class":"text-ellipsis css-jgjrt"}).text

    return self.searchTitle(title)
