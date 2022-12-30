import json

from typing import Final, List
from urllib import parse

from src.exception import WrongPageException

from .novel_platform import Platform
from .result import Result, PlatformType

TITLE_QUERY: Final[
    str
] = """
query SearchKeyword($input: SearchKeywordInput!) {
  searchKeyword(searchKeywordInput: $input) {     
    list {
      ...NormalListViewItem
    }
  }
}

fragment NormalListViewItem on NormalListViewItem {
  scheme
}
"""

LINK_QUERY: Final[
    str
] = """
query contentHomeOverview($seriesId: Long!) {
  contentHomeOverview(seriesId: $seriesId) {
    content {
      ...SeriesFragment
    }
  }
}

fragment SeriesFragment on Series {
  seriesId
  title
  thumbnail
  category
  subcategory
  badge
  ageGrade
  state
  onIssue
  authors
  serviceProperty {
    viewCount
  }
}
"""

BOOK_QUERY: Final[
    str
] = """
query contentHomeProductList($after: String, $before: String, $first: Int, $last: Int, $seriesId: Long!, $boughtOnly: Boolean, $sortType: String) {
  contentHomeProductList(
    seriesId: $seriesId
    after: $after
    before: $before
    first: $first
    last: $last
    boughtOnly: $boughtOnly
    sortType: $sortType
  ) {
    totalCount
  }
}
"""


class Kakaopage(Platform):
    def __init__(self) -> None:
        super().__init__()
        self.SEARCHLINK: Final[str] = "https://page.kakao.com/graphql"

    def __searchTitleBody(self, text: str):
        return {
            "query": TITLE_QUERY,
            "operationName": "SearchKeyword",
            "variables": {"input": {"size": 100, "keyword": text, "categoryUid": "11"}},
        }

    def __searchLinkBody(self, serial: int):
        return {
            "query": LINK_QUERY,
            "operationName": "contentHomeOverview",
            "variables": {"seriesId": serial},
        }

    def __searchBookBody(self, serial: int):
        return {
            "query": BOOK_QUERY,
            "operationName": "contentHomeProductList",
            "variables": {"seriesId": serial, "boughtOnly": False},
        }

    async def __parseResult(self, novel_content) -> Result:
        content = novel_content["data"]["contentHomeOverview"]["content"]

        serial = content["seriesId"]
        title = content["title"]
        thumbnail = "https:" + content["thumbnail"]

        view = content["serviceProperty"]["viewCount"]
        good = 0
        book = await self.__searchCount(serial)

        link = f"https://page.kakao.com/content/{serial}"
        author = content["authors"]

        is_end = content["onIssue"] == "End"
        is_plus = True
        age_limit = (
            0
            if content["ageGrade"] == "All"
            else 15
            if content["ageGrade"] == "Fifteen"
            else 19
        )

        return Result(
            title=title,
            thumbnail=thumbnail,
            type=PlatformType.KAKAOPAGE,
            view=view,
            good=good,
            book=book,
            link=link,
            author=author,
            is_end=is_end,
            is_plus=is_plus,
            age_limit=age_limit,
        )

    async def __searchCount(self, serial: int):
        content = json.loads(
            await self._postContent(
                self.SEARCHLINK, data=json.dumps(self.__searchBookBody(serial))
            )
        )
        return content["data"]["contentHomeProductList"]["totalCount"]

    # 소설 제목으로 검색
    async def searchTitle(self, title: str) -> List[Result]:
        content = json.loads(
            await self._postContent(
                self.SEARCHLINK, data=json.dumps(self.__searchTitleBody(title))
            )
        )

        clst = content["data"]["searchKeyword"]["list"]
        novel_content_list = [x["scheme"].split("?series_id=")[-1] for x in clst]

        return [await self.searchURL(series_id) for series_id in novel_content_list]

    # 소설 링크로 검색
    async def searchURL(self, url: str) -> Result:
        serial = int(url.split("/")[-1])
        content = json.loads(
            await self._postContent(
                self.SEARCHLINK, data=json.dumps(self.__searchLinkBody(serial))
            )
        )

        return self.__parseResult(content)
