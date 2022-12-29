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

from typing import List

from src.app import NovelStatistics
from src.platform import Result, Tag as ResultTag
from src.db import session, Novel, NovelInfo, Episode, Tag

from sqlalchemy import func

app = NovelStatistics(only_link=True)

def commitTag(tags: List[ResultTag]):
  tagLst = []
  for tag in tags:
    dbTag = session.query(Tag).filter(Tag.name == tag.name).one_or_none()
    if dbTag != None:
      tagLst.append(dbTag)
    else:
      t = Tag(**tag.data)
      tagLst.append(t)
      session.add(t)
  
  session.commit()

  [session.refresh(t) for t in tagLst]

  return tagLst

async def addInfo(message: bytes):
  body = json.loads(message.decode())
  _id, _link = body["id"], body["link"]

  result: Result = await app.search(_link)

  if result == None:
    print(f"[{_id}] - \"{_link}\" (미사용으로 전환)")
    session.query(Novel).filter(
      Novel.id == _id
    ).update({
      "is_able": False
    })

  else:
    print(f"[{_id}] - \"{result.title}\"")

    tagLst = commitTag(result.tags)

    session.query(Novel).filter(
      Novel.id == _id
    ).update({
      "title": result.title,
      "thumbnail": result.thumbnail,
      "description": result.description,
      "is_end": result.is_end,
      "is_plus": result.is_plus,
      "age_limit": result.age_limit,
    })
  
    novel = session.query(Novel).filter(Novel.id == _id).one()
    novel.tags = tagLst

    info = NovelInfo(view=result.view, good=result.good, book=result.book, novel_id=_id)
    session.add(info)

    episode = await app.searchEpisode(_link)

    rep = session.query(func.max(Episode.idx)).filter_by(novel_id = _id).scalar()

    for ep in episode:
      if ep.idx <= rep:
        session.query(Episode).filter(Episode.novel_id == _id, Episode.idx == ep.idx).update(ep.data)
      else:
        session.add(
          Episode(
            **ep.data,
            novel_id=_id
          )
        )

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