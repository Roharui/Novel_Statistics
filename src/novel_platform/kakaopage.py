import json

from typing import Final, List
from urllib import parse

from novel_platform.result.result import PlatformType

from .novel_platform import Platform
from .result import Result

class Kakaopage(Platform):
  def __init__(self) -> None:
    super().__init__()
    self.SEARCHLINK: Final[str] =  "https://api2-page.kakao.com/api/v5/store/search"

  async def __parseResult(self, novel_content) -> Result:
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

  # 소설 제목으로 검색
  async def searchTitle(self, title: str) -> List[Result]:
    word = f"word={parse.quote(title)}"
    content = json.loads(await self._postContent(self.SEARCHLINK, data=word))

    novel_content_list = content["results"][2]["items"]

    return [self.__parseResult(novel_content) for novel_content in novel_content_list]

  # 소설 링크로 검색
  async def searchURL(self, url: str) -> Result:
    content = await self._getContentParser(url)

    title = content.find("h2", {"class":"text-ellipsis css-jgjrt"}).text

    word = f"word={parse.quote(title)}"
    content = json.loads(self._postContent(self.SEARCHLINK, data=word))

    novel_content = content["results"][2]["items"][0]

    return await self.__parseResult(novel_content)
