
import os 
import argparse
import psycopg2
import asyncio

from src import NovelStatic
from dotenv import load_dotenv

from src.novel_platform.result.result import Result

load_dotenv()

class DB:
  def __init__(self) -> None:
    self.conn = psycopg2.connect(
      host=os.environ.get("host"), 
      dbname=os.environ.get("dbname"), 
      user=os.environ.get("user"), 
      password=os.environ.get("password"), 
      port=os.environ.get("port")
    )

  def do(self, result: Result) -> None:
    cur = self.conn.cursor()

    cur.execute(
      """
      do $$
      declare
        _title varchar := %s;
        _type novel_type_enum := %s;
        _thumbnail text := %s;
        _link varchar := %s;
        _view int := %s;
        _good int := %s;
        _book int := %s;
        
        _ori_title varchar;
        _ori_thumbnail varchar;
        _id int;
      begin
        select title, thumbnail, id into _ori_title, _ori_thumbnail, _id from novel n where n.link = _link;
        if not exists (select 1 from novel n where n.link = _link) then
          INSERT INTO "novel"("createdAt", "updatedAt", "title", "type", "thumbnail", "link") 
              VALUES 
              (DEFAULT, DEFAULT, _title, _type, _thumbnail, _link);
            select id into _id from novel n where n.link = _link;
        end if;

        if _ori_title <> _title or _ori_thumbnail <> _thumbnail then 
          UPDATE "novel" SET 
              "title" = _title, 
              "thumbnail" = _thumbnail
              WHERE "link" = _link;
            end if;
          
          INSERT INTO "novel-info"("createdAt", "updatedAt", "view", "good", "book", "novelId") 
          VALUES 
          (DEFAULT, DEFAULT, _view, _good, _book, _id);
        
      end $$;
      """, 
      (result.title, result.type.value, result.thumbnail, result.link, result.view, result.good, result.book)
    )
    self.conn.commit()

    cur.close()

  def close(self):
    self.conn.close()
  

async def main():
  parser = argparse.ArgumentParser(description="소설 통계 프로그램")

  parser.add_argument("input", help="소설 제목 혹은 링크")

  args = parser.parse_args()

  result = await NovelStatic(args.input).search()

  db = DB()

  db.do(result)

  db.close()
  
if __name__ == '__main__':
  asyncio.run(main())