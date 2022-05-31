
import os 
import argparse
import psycopg2
import asyncio

from src import NovelStatic
from dotenv import load_dotenv

load_dotenv()

async def main():
  parser = argparse.ArgumentParser(description="소설 통계 프로그램")

  parser.add_argument("input", help="소설 제목 혹은 링크")

  args = parser.parse_args()

  result = await NovelStatic(args.input).search()

  conn = psycopg2.connect(
    host=os.environ.get("host"), 
    dbname=os.environ.get("dbname"), 
    user=os.environ.get("user"), 
    password=os.environ.get("password"), 
    port=os.environ.get("port")
  )

  cur = conn.cursor()

  cur.execute(
    """
    INSERT INTO "novel"("createdAt", "updatedAt", "title", "type", "thumbnail", "view", "good", "book", "link") 
    VALUES (DEFAULT, DEFAULT, %s, %s, %s, %s, %s, %s, %s) RETURNING "id", "createdAt", "updatedAt", "type" 
    """, 
    (result.title, result.type.value, result.thumbnail, result.view, result.good, result.book, result.link)
  )
  conn.commit()

  cur.close()
  conn.close()
  
if __name__ == '__main__':
  asyncio.run(main())