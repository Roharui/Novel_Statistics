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
    async with sem:
        return await publish(channel, item)

async def main() -> None:
  try:
    connection = await aio_pika.connect(os.environ.get("MQ_URL"))

    async with connection:
      channel = await connection.channel()

      p = [safe_publish(channel, item) for item in session.query(Novel).all()]

      await asyncio.gather(*p)
  except KeyboardInterrupt as e:
    exit(0)


if __name__ == "__main__":
  import argparse

  parser = argparse.ArgumentParser(description="소설 통계 프로그램 프로듀서")

  parser.add_argument("--now", required=False, default=False, help="바로 시작")
  parser.add_argument("--start", required=False, default="0:00", help="프로그램 시작 시간")

  args = parser.parse_args()

  if args.now:
    asyncio.run(main())
  else:
    import aioschedule as schedule
    from time import sleep

    schedule.every().day.at(args.start).do(main)

    loop = asyncio.get_event_loop()

    print(f" [x] 소설 크롤링 프로듀서가 실행되었습니다. 이 프로그램의 작동 시각은 [{args.start}] 입니다.")
    
    while True:
      loop.run_until_complete(schedule.run_pending())
      sleep(0.1)
