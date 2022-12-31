import traceback

from .logger import log


class WrongLinkException(Exception):
    def __init__(self, link: str, info: str = "잘못된 주소입니다") -> None:
        self.link = link
        self.info = info

    def log(self):
        text = f"{self.info} - {self.link}"
        log(text)


class WrongPageException(Exception):
    def __init__(self, info: str = "잘못된 페이지입니다", url: str = None) -> None:
        self.info = info
        self.url = url

    def log(self):
        text = f"{self.info} - {self.url}"
        log(text, traceback.format_exc())
