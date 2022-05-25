
class WrongLinkException(Exception):
  def __str__(self):
    return "링크가 올바르지 않습니다."