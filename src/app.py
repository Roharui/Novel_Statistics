import asyncio

from typing import Dict, List, Union
from urllib.parse import urlparse
from validators import url as checkURL

from src.exception import WrongPageException, WrongLinkException
from src.platform import Result, Episode, Novelpia, Munpia, Kakaopage, Platform

from itertools import chain

PLATFORM: Dict[str, Platform] = {
    "novelpia.com": Novelpia(),
    "novel.munpia.com": Munpia(),
    # "page.kakao.com": Kakaopage()
}


class NovelStatistics:
    def __init__(self, only_link: bool = False) -> None:
        self.only_link = only_link

    async def search(self, __input: str) -> Union[Result, List[Result], None]:
        url = None
        title = None

        if checkURL(__input):
            url = __input
        else:
            title = __input

        try:
            # 이름 일 경우
            if title:
                if self.only_link:
                    raise WrongLinkException(url, "오직 링크만 입력이 가능합니다.")
                coroutine = await asyncio.gather(
                    *[engin.searchTitle(title) for engin in PLATFORM.values()]
                )
                result = await asyncio.gather(*chain(*coroutine))
                return result
            # 링크일 경우
            else:
                host = urlparse(url).hostname

                if not host in PLATFORM.keys():
                    raise WrongLinkException(url)

                engin: Platform = PLATFORM[host]

                return await engin.searchURL(url)

        except (WrongLinkException, WrongPageException) as e:
            e.log()

    async def searchRecentLink(self) -> List[Result]:
        try:
            coroutine = await asyncio.gather(
                *[engin.searchRecentLink() for engin in PLATFORM.values()]
            )
            return list(chain(*coroutine))
        except (WrongLinkException, WrongPageException) as e:
            e.log()
            return []

    async def searchEpisode(self, url: str) -> List[Episode]:
        host = urlparse(url).hostname
        try:
            if not checkURL(url) or not host in PLATFORM.keys():
                raise WrongLinkException(url)
            engin: Platform = PLATFORM[host]
            return await engin.searchEpisode(url)
        except (WrongLinkException, WrongPageException) as e:
            e.log()
            return []
