import asyncio
import json
import logging

from typing import Dict, Union

from aio_pika import Message, connect
from aio_pika.abc import AbstractIncomingMessage

from src import NovelStatic
from db import DB
from src.exception.wrong_link_exception import WrongLinkException
from src.exception.wrong_page_exception import WrongPageException

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

          response = await do(n)

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
          

async def do(request: Dict[str, str]) -> Dict[str, Union[int, str, None]]:

  if not "link" in request.keys():
    return  {
      "response": 404,
      "err": "값이 없습니다"
    }
  
  link = request["link"]

  print("[X] 수신 성공 - {}".format(link))

  try:
    result = await crawler.search(link)
  except WrongLinkException as e:
    print("[X] 크롤링 실패 (잘못된 링크) - {}".format(link))
    return {
      "response": 403,
      "err": str(e)
    }
    
  except WrongPageException as e:
    print("[X] 크롤링 실패 (잘못된 페이지) - {}".format(link))
    return {
      "response": 403,
      "err": str(e)
    }

  if result is None:
    print("[X] 크롤링 실패 (잘못된 값) - {}".format(link))
    return {
      "response": 404,
      "err": "링크가 아닙니다"
    }
    
  
  print("[X] 크롤링 성공 - {}".format(link))
  db.do(result)
  print("[X] DB 갱신 성공 - {}".format(link))

  return {
    "response": 200,
    "err": None
  }


if __name__ == "__main__":
  asyncio.run(main())