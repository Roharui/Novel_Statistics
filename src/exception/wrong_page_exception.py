
class WrongPageException(Exception):
  def __str__(self):
    return "페이지가 올바르지 않습니다."