import asyncio
import aio_pika
import aio_pika.abc

from src import NovelStatic
from db import DB

QUEUE = "novel.link"

crawler = NovelStatic(only_link=True)

db = DB()

async def main(loop):
  print("[X] 컨슈머 작동 시작")

  connection = await aio_pika.connect_robust(
      "amqp://guest:guest@127.0.0.1/", loop=loop
  )

  async with connection:

    # Creating channel
    channel: aio_pika.abc.AbstractChannel = await connection.channel()

    # Declaring queue
    queue: aio_pika.abc.AbstractQueue = await channel.declare_queue(
        QUEUE
    )

    async with queue.iterator() as queue_iter:
      # Cancel consuming after __aexit__
      async for message in queue_iter:
        async with message.process():
          link = message.body.decode()
          await do(link)
          

async def do(link: str):
  print("[X] 수신 성공 - {}".format(link))
  result = await crawler.search(link)

  if result is None:
    print("[X] 크롤링 실패 (잘못된 값) - {}".format(link))
    return
  
  print("[X] 크롤링 성공 - {}".format(link))
  db.do(result)
  print("[X] DB 갱신 성공 - {}".format(link))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()