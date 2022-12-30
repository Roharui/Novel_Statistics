import json

import datetime
from pytz import timezone

from typing import Final, List, Union
from urllib import parse

from src.exception import WrongPageException

from .novel_platform import Platform
from .result import Result, PlatformType, Episode, Tag


class Novelpia(Platform):
    def __init__(self) -> None:
        super().__init__()
        self.SEARCHLINK: Final[str] = "https://novelpia.com/proc"
        self.NOVELLINK: Final[str] = "https://novelpia.com/novel"
        self.PLUSLINK: Final[str] = "https://novelpia.com/plus"
        self.EPSODELINK: Final[str] = "https://novelpia.com/proc/episode_list"

    def __searchURL(self, word: str) -> str:
        word = parse.quote(word)
        return f"{self.SEARCHLINK}/novelsearch/{word}"

    def __novelURL(self, num: Union[int, str]) -> str:
        return f"{self.NOVELLINK}/{num}"

    # 해당 소설의 에피소드 일람
    async def searchEpisode(self, url: str) -> List[Episode]:
        novel_no = url.split("/")[-1]
        page = 0
        max_page = 1

        content = None

        result = []

        # TODO 후일 비동기 적으로 변경할 것

        while True:
            try:
                content = await self._postContentParser(
                    self.EPSODELINK, f"novel_no={novel_no}&page={page}", json=False
                )

                epLst = content.find_all("tr", {"class": "ep_style5"})

                for ep in epLst:

                    _, td2, td3 = ep.find_all("td")

                    if td2.find("span") == None:
                        break

                    [span.extract() for span in td2.find("b").find_all("span")]

                    title = td2.find("b").text.strip()

                    td2.find("b").extract()

                    idx = len(result) + 1

                    td2.find("span").extract()

                    numbers = td2.find("span")

                    number_text = [
                        int("".join(i for i in x if i.isdigit()))
                        for x in numbers.text.replace(",", "")
                        .replace("\xa0", "")
                        .split(" ")
                        if len(x.strip())
                    ]

                    word_size, view, comment, good = [0, 0, 0, 0]

                    for i, num in zip(numbers.find_all("i"), number_text):
                        if "ion-document-text" in i["class"]:
                            word_size = num
                        elif "ion-android-people" in i["class"]:
                            view = num
                        elif "ion-chatbox-working" in i["class"]:
                            comment = num
                        elif "ion-thumbsup" in i["class"]:
                            good = num

                    cur_date = datetime.datetime.now(timezone("Asia/Seoul"))

                    if td3.text.find("전") >= 0:
                        date = str(
                            datetime.datetime(
                                cur_date.year, cur_date.month, cur_date.day
                            )
                        )
                    else:
                        date_info = [int(x) for x in td3.text.split(".")]

                        if len(date_info) < 3:
                            date_info.insert(0, cur_date.year)
                        else:
                            date_info[0] += 2000

                        date = str(datetime.datetime(*date_info))

                    result.append(
                        Episode(
                            idx=idx,
                            title=title,
                            word_size=str(word_size),
                            view=view,
                            comment=comment,
                            good=good,
                            date=date,
                        )
                    )

                page += 1

                nxtPage = content.find_all("li", {"class": "page-item"})

                max_page = max(
                    [
                        int(p.find("div", {"class": "page-link"}).text)
                        for p in nxtPage[1:-1]
                    ]
                )

                if page >= max_page:
                    break

            except Exception as e:
                raise WrongPageException("파싱에 오류가 발생하였습니다.")

        return result

    # 최근에 올라온 소설 링크
    async def searchRecentLink(self) -> List[str]:
        content = await self._getContentParser(self.PLUSLINK)

        return [
            self.__novelURL(
                next(filter(lambda a: a.find("novel_") >= 0, item["class"])).split("_")[
                    -1
                ]
            )
            for item in content.find_all("div", {"class": "novelbox"})
        ]

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

        try:
            novel_content = (
                content.find("div", {"class": "mobile_hidden s_inv"})
                .find("div")
                .find("table")
            )
            number_data = novel_content.find_all("tr")[2].find("div").find("font").text

            thumbnail_wrap = novel_content.find("tr").find("td").find(
                "a"
            ) or novel_content.find("tr").find("td")

            thumbnail = None
            if not thumbnail_wrap is None:
                thumbnail = "https:" + thumbnail_wrap.find("img")["src"].strip()

                thumbnail = (
                    None if thumbnail == "https://image.novelpia.com" else thumbnail
                )

            description = novel_content.find_all("font", {"class": "font11"})[1].text

            tags = [
                Tag(name=tag.text)
                for tag in novel_content.find_all("div")[-1].find_all("span")
            ][:-1]

            is_end = not not (novel_content.find("span", {"class": "b_comp"}))
            is_plus = not not (novel_content.find("span", {"class": "b_plus"}))

            age_limit = (
                19
                if novel_content.find("span", {"class": "b_19"})
                else 15
                if novel_content.find("span", {"class": "b_15"})
                else 0
            )

            title = novel_content.find("tr").find_all("td")[1].find("span").text

            author = (
                novel_content.find("tr")
                .find_all("td")[1]
                .find_all("font")[1]
                .find("a")
                .text
            )

            number_text = [
                int("".join(i for i in x if i.isdigit()))
                for x in number_data.replace(",", "").replace("\xa0", "").split(" ")
                if len(x)
            ]
            view, book, good = number_text

        except Exception as e:
            raise WrongPageException("파싱에 오류가 발생하였습니다.")

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
            author=author,
            description=description,
            tags=tags,
        )
