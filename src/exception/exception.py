from datetime import datetime

from .logger import log

class WrongLinkException(Exception):
  def __init__(self, link: str, info: str = "잘못된 주소입니다", ex_info = None) -> None:
    self.link = link
    self.info = info
    self.ex_info = ex_info

  def log(self):
    text = f"[{datetime.now()}] {self.info} - {self.link}"
    if self.ex_info != None:
      text += f"\n{self.ex_info}"
    log(
      text
    )

class WrongPageException(Exception):
  def __init__(self, content: str, info: str = "잘못된 페이지입니다", ex_info = None) -> None:
    self.content = content
    self.info = info
    self.ex_info = ex_info

  def log(self):
    lst = [
      f"[{datetime.now()}] {self.info}",
      "===",
      f"{self.content}"
      "===",
    ]
    if self.ex_info != None:
      lst += [
        str(self.ex_info),
        "==="
      ]
    log(
      "\n"
      .join(lst)
    )