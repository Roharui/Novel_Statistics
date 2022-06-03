import asyncio
import json
import logging

from aio_pika import Message, connect
from aio_pika.abc import AbstractIncomingMessage

from src import NovelStatic
from db import DB
from src.exception.wrong_link_exception import WrongLinkException

QUEUE = "novel.link"

crawler = NovelStatic(only_link=True)

db = DB()

async def main() -> None:
  # Perform connection
  connection = await connect("amqp://guest:guest@localhost/")

  # Creating a channel
  channel = await connection.channel()
  exchange = channel.default_exchange

  # Declaring queue
  queue = await channel.declare_queue(QUEUE)

  print(" [x] Awaiting RPC requests")

  # Start listening the queue with name 'hello'
  async with queue.iterator() as qiterator:
    message: AbstractIncomingMessage
    async for message in qiterator:
      try:
        async with message.process(requeue=False):
          assert message.reply_to is not None

          n = json.loads(message.body.decode())

          response = {
            "code": 200
          }

          if not "link" in n.keys():
            response["code"] = 400
          else:
            if not await do(n["link"]):
              response["code"] = 500

          await exchange.publish(
            Message(
              body=json.dumps(response).encode(),
              correlation_id=message.correlation_id,
            ),
            routing_key=message.reply_to,
          )
          print("Request complete")
      except Exception:
        logging.exception("Processing error for message %r", message)
          

async def do(link: str) -> bool:
  print("[X] 수신 성공 - {}".format(link))

  try:
    result = await crawler.search(link)
  except WrongLinkException as e:
    print("[X] 크롤링 실패 (잘못된 링크) - {}".format(link))
    return False

  if result is None:
    print("[X] 크롤링 실패 (잘못된 값) - {}".format(link))
    return False
  
  print("[X] 크롤링 성공 - {}".format(link))
  db.do(result)
  print("[X] DB 갱신 성공 - {}".format(link))

  return True


if __name__ == "__main__":
  asyncio.run(main())