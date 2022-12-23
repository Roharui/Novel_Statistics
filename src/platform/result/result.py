
from enum import Enum

class PlatformType(Enum):
  NOVELPIA="novelpia"
  MUNPIA="munpia"
  KAKAOPAGE="kakaopage"

class Result:
  def __init__(self, **kwargs) -> None:
    self.title: str = kwargs["title"]
    self.type: PlatformType = kwargs["type"]
    self.thumbnail: str = kwargs["thumbnail"]
    self.view: int = kwargs["view"]
    self.good: int = kwargs["good"]
    self.book: int = kwargs["book"]
    self.link: str = kwargs["link"]
    self.author: str = kwargs["author"]
    self.description: str = kwargs["description"]
    self.is_end: bool = kwargs["is_end"]
    self.is_plus: bool = kwargs["is_plus"]
    self.age_limit: int = kwargs["age_limit"]
    self.data = kwargs

  def __str__(self) -> str:
    return str(self.data)

  def __repr__(self) -> str:
    return str(self.data)

class Episode:
  def __init__(self, **kwargs) -> None:
    self.idx: int = kwargs["idx"]
    self.title: str = kwargs["title"]
    self.word_size: str = kwargs["word_size"]
    self.view: int = kwargs["view"]
    self.good: int = kwargs["good"]
    self.comment: int = kwargs["comment"]
    self.date: str = kwargs["date"]
    self.data = kwargs

  def __str__(self) -> str:
    return str(self.data)

  def __repr__(self) -> str:
    return str(self.data)