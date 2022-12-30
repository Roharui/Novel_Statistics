import os

from datetime import datetime, timezone

from discord_webhook import DiscordWebhook

__all__ = ["log"]


def fileInput(info: str, err: str = None) -> None:
    with open(os.environ.get("FILE_NAME"), "a", encoding="utf8") as f:
        f.write(f"[{datetime.now(timezone('Asia/Seoul'))}] {info}\n")
        if err != None:
            f.write(f"{err}\n")


webhook = os.environ.get("WEBHOOK")


def discord(info: str, err: str = None) -> None:
    text = f"[{datetime.now(timezone('Asia/Seoul'))}] {info}"
    if err != None:
        text += f"\n```\n{err}\n```"

    DiscordWebhook(url=webhook, content=text).execute()


def printLog(info: str, err: str = None) -> None:
    text = f"[{datetime.now(timezone('Asia/Seoul'))}] {info}"
    if err != None:
        text += f"\n```\n{err}\n```"
    print(text)


log_method = {
    "PRINT": print,
    "FILE": fileInput,
    "DISCORD": discord,
    None: print,
}

log = log_method[os.environ.get("LOG")]
