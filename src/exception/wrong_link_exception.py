
class WrongLinkException(Exception):
  def __str__(self):
    return "사이트 링크가 올바르지 않습니다."