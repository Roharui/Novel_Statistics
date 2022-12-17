import os

__all__ = ["log"]

def fileInput(text: str) -> None:
  with open(os.environ.get("FILE_NAME"), "a", encoding="utf8") as f:
    f.write(text + "\n")

log_method = {
  "PRINT": print,
  "FILE": fileInput,
  None: print,
}

log = log_method[os.environ.get("LOG")]