import asyncio
import aio_pika
import aio_pika.abc

QUEUE = "novel.link"

async def main(loop):
  # Explicit type annotation
  connection: aio_pika.RobustConnection = await aio_pika.connect_robust(
      "amqp://guest:guest@127.0.0.1/", loop=loop
  )

  routing_key = QUEUE

  channel: aio_pika.abc.AbstractChannel = await connection.channel()

  await channel.default_exchange.publish(
      aio_pika.Message(
          body='https://novelpia.com/novel/96189'.encode()
      ),
      routing_key=routing_key
  )

  await connection.close()


if __name__ == "__main__":
  loop = asyncio.get_event_loop()
  loop.run_until_complete(main(loop))
  loop.close()