
from enum import Enum, auto

class PlatformType(Enum):
  NOVELPIA=auto()

class Result:
  def __init__(self, **kwargs) -> None:
    self.title: str = kwargs["title"]
    self.type: PlatformType = kwargs["type"]
    self.thumbnail: str = kwargs["thumbnail"]
    self.view: int = kwargs["view"]
    self.good: int = kwargs["good"]
    self.book: int = kwargs["book"]
    self.data = kwargs

  def __str__(self) -> str:
    return str(self.data)