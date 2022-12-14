from dotenv import load_dotenv

load_dotenv()

import os

import asyncio
import aio_pika

import json

from db import session, Novel

sem = asyncio.Semaphore(10)

QUEUE = os.environ.get("MQ_QUEUE")

async def publish(channel, item: Novel):
  print(f"[{item.id}] - \"{item.title}\"")
  await channel.default_exchange.publish(
    aio_pika.Message(json.dumps({"id": item.id, "link": item.link}).encode()),
    routing_key=QUEUE
  )

async def safe_publish(channel, item: Novel):
    async with sem:  # semaphore limits num of simultaneous downloads
        return await publish(channel, item)

async def main() -> None:
  connection = await aio_pika.connect(os.environ.get("MQ_URL"))

  async with connection:
    channel = await connection.channel()

    p = [safe_publish(channel, item) for item in session.query(Novel).all()]

    await asyncio.gather(*p)


if __name__ == '__main__':
  asyncio.run(main())