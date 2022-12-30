from dotenv import load_dotenv

load_dotenv()

import os

import asyncio
import aio_pika

import json

from src.db import session, Novel

sem = asyncio.Semaphore(10)

QUEUE = os.environ.get("MQ_QUEUE")


async def publish(channel, item: Novel):
    print(f'[{item.id}] - "{item.title}"')
    await channel.default_exchange.publish(
        aio_pika.Message(json.dumps({"id": item.id, "link": item.link}).encode()),
        routing_key=QUEUE,
    )


async def safe_publish(channel, item: Novel):
    async with sem:
        await publish(channel, item)
        await asyncio.sleep(10)
        return


async def main() -> None:
    MQ_URL = os.environ.get("MQ_URL")

    if MQ_URL == None:
        print("URL이 존재하지 않습니다. .env 파일을 확인해주세요.")
        return

    connection = await aio_pika.connect(MQ_URL)

    async with connection:
        channel = await connection.channel()

        novels = (
            session.query(Novel).filter(Novel.is_able == True).order_by(Novel.id).all()
        )

        await asyncio.gather(*[safe_publish(channel, x) for x in novels])


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="소설 통계 프로그램 프로듀서")

    parser.add_argument(
        "--now", required=False, default=False, help="바로 시작", action="store_true"
    )
    parser.add_argument("--start", required=False, default="0:00", help="프로그램 시작 시간")

    args = parser.parse_args()
    loop = asyncio.get_event_loop()

    if args.now:
        loop.run_until_complete(main())
    else:
        import aioschedule as schedule
        from time import sleep

        schedule.every().day.at(args.start).do(main)

        print(f" [x] 소설 크롤링 프로듀서가 실행되었습니다. 이 프로그램의 작동 시각은 [{args.start}] 입니다.")

        while True:
            loop.run_until_complete(schedule.run_pending())
            sleep(0.1)
