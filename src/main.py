import argparse
import platform

from typing import Dict
from urllib.parse import urlparse
from validators import url


PLATFORM: Dict[str, platform.Platform] = {
  "novelpia.com" : platform.Novelpia()
}

class NovelStatic:
  def __init__(self, __input: str) -> None:
    self.title = None
    self.url = None

    if url(__input):
      self.url = __input
    else:
      self.title = __input

  def search(self):
    # 이름 일 경우
    if self.title:
      pass
    # 링크일 경우
    else:
      host = urlparse(self.url).hostname
      engin: platform.Platform = None

      try:
        engin = PLATFORM[host]
      except Exception as e:
        print("잘못된 링크입니다")
        return

      engin.searchURL(self.url)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="소설 통계 프로그램")

  parser.add_argument("input", help="소설 제목 혹은 링크")

  args = parser.parse_args()

  NovelStatic(args.input).search()

  