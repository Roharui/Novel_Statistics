import os

import asyncio
import json
import uuid
from typing import MutableMapping

from aio_pika import Message, connect
from aio_pika.abc import (
  AbstractChannel, AbstractConnection, AbstractIncomingMessage, AbstractQueue,
)

from db import DB

QUEUE = "novel.link"
class UpdateDBClient:
  connection: AbstractConnection
  channel: AbstractChannel
  callback_queue: AbstractQueue
  loop: asyncio.AbstractEventLoop

  def __init__(self) -> None:
    self.futures: MutableMapping[str, asyncio.Future] = {}
    self.loop = asyncio.get_running_loop()

  async def connect(self) -> "UpdateDBClient":
    self.connection = await connect(
      os.environ.get("MQ_URL"), loop=self.loop,
    )
    self.channel = await self.connection.channel()
    self.callback_queue = await self.channel.declare_queue(exclusive=True)
    await self.callback_queue.consume(self.on_response)

    return self

  def on_response(self, message: AbstractIncomingMessage) -> None:
    if message.correlation_id is None:
      print(f"Bad message {message!r}")
      return

    future: asyncio.Future = self.futures.pop(message.correlation_id)
    future.set_result(message.body)

  async def call(self, n: str):
    body = json.dumps({"link": n})
    correlation_id = str(uuid.uuid4())
    future = self.loop.create_future()

    self.futures[correlation_id] = future

    await self.channel.default_exchange.publish(
      Message(
        body.encode(),
        content_type="text/plain",
        correlation_id=correlation_id,
        reply_to=self.callback_queue.name,
      ),
      routing_key=QUEUE,
    )

    return await future


async def main() -> None:

  db = DB(os.environ.get("DB_URL"))
  
  links = db.getUrls()
  rpc = await UpdateDBClient().connect()
  
  for link in links:
    print(f" [x] Requesting... {link}")
    response = await rpc.call(link)
    print(f" [.] Got {response!r}")


if __name__ == "__main__":
  import argparse

  parser = argparse.ArgumentParser(description="소설 통계 프로그램 컨슈머")

  parser.add_argument("--env", required=False, default=".env", help="env 변수 파일 위치")
  parser.add_argument("--now", required=False, default=False, help="바로 시작")
  parser.add_argument("--start", required=False, default="0:00", help="프로그램 시작 시간")

  args = parser.parse_args()

  from dotenv import load_dotenv

  load_dotenv(
    dotenv_path=args.env
  )

  if args.now:
    asyncio.run(main())
  else:
    import aioschedule as schedule
    from time import sleep

    schedule.every().day.at(args.start).do(main)

    loop = asyncio.get_event_loop()

    print(f" [x] 실행되었습니다. 이 프로그램의 작동 시각은 [{args.start}] 입니다.")

    while True:
        loop.run_until_complete(schedule.run_pending())
        sleep(0.1)