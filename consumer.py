from dotenv import load_dotenv

load_dotenv()

import os
import logging

import aio_pika
import json

import asyncio
import platform

if platform.system()=='Windows':
  asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from src.app import NovelStatic
from src.novel_platform.result import Result
from db import session, Novel, NovelInfo

app = NovelStatic(only_link=True)

async def addInfo(message: bytes):
  body = json.loads(message.decode())
  _id, _link = body["id"], body["link"]

  result: Result = await app.search(_link)

  print(f"[{_id}] - \"{result.title}\"")

  session.query(Novel).filter(
    Novel.id == _id
  ).update({
    "title": result.title,
    "thumbnail": result.thumbnail,
    "is_end": result.is_end,
    "is_plus": result.is_plus,
    "age_limit": result.age_limit,
  })

  info = NovelInfo(view=result.view, good=result.good, book=result.book, novel_id=_id)
  session.add(info)
  
  session.commit()

async def main() -> None:
  connection = await aio_pika.connect_robust(
    os.environ.get("MQ_URL"),
  )

  queue_name = os.environ.get("MQ_QUEUE")

  async with connection:
    # Creating channel
    channel = await connection.channel()

    # Will take no more than 10 messages in advance
    await channel.set_qos(prefetch_count=10)

    # Declaring queue
    queue = await channel.declare_queue(queue_name, auto_delete=True)

    async with queue.iterator() as queue_iter:
      async for message in queue_iter:
        async with message.process():
          await addInfo(message.body)

if __name__ == "__main__":
  logging.basicConfig(level=logging.WARNING)
  
  print(f" [x] 소설 크롤링 컨슈머가 실행되었습니다.")

  loop = asyncio.get_event_loop()

  loop.run_until_complete(main())