import argparse

import platform

from typing import Dict, List, Union
from urllib.parse import urlparse
from validators import url
from exception import WrongLinkException

from platform.result import Result

PLATFORM: Dict[str, platform.Platform] = {
  "novelpia.com" : platform.Novelpia(),
  "novel.munpia.com": platform.Munpia(),
  "page.kakao.com": platform.Kakaopage()
}

class NovelStatic:
  def __init__(self, __input: str) -> None:
    self.title = None
    self.url = None

    if url(__input):
      self.url = __input
    else:
      self.title = __input

  def search(self) -> Union[Result, List[Result]]:
    # 이름 일 경우
    if self.title:
      result = []
      for i in [engin.searchTitle(self.title) for engin in PLATFORM.values()]:
        result += i
      return result
    # 링크일 경우
    else:
      host = urlparse(self.url).hostname
      engin: platform.Platform = None

      try:
        engin = PLATFORM[host]
      except Exception as e:
        raise WrongLinkException()

      return engin.searchURL(self.url)

def main():
  parser = argparse.ArgumentParser(description="소설 통계 프로그램")

  parser.add_argument("input", help="소설 제목 혹은 링크")

  args = parser.parse_args()

  NovelStatic(args.input).search()
  
if __name__ == '__main__':
  main()