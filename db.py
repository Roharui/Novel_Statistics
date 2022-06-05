
import os 
import argparse
import psycopg2
import asyncio

from src import NovelStatic, Result

from dotenv import load_dotenv

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
      f"""
      do $$
      declare
        _title varchar := '{result.title}';
        _type novel_type_enum := '{result.type.value}';
        _thumbnail text := '{result.thumbnail}';
        _link varchar := '{result.link}';
        _view int := '{result.view}';
        _good int := '{result.good}';
        _book int := '{result.book}';

        _is_end bool := {"true" if result.is_end else "false"};
        _age_limit int := {result.age_limit};
        _author varchar := '{result.author}';
        
        _ori_title varchar;
        _ori_thumbnail varchar;
        _ori_is_end bool;
        _id int;
      begin
        select title, thumbnail, id, is_end into _ori_title, _ori_thumbnail, _id, _ori_is_end from novel n where n.link = _link;

        if not exists (select 1 from novel n where n.link = _link) then
          INSERT INTO "novel"("createdAt", "updatedAt", "title", "type", "thumbnail", "link", "is_end", "age_limit", "author") 
          VALUES 
          (DEFAULT, DEFAULT, _title, _type, _thumbnail, _link, _is_end, _age_limit, _author);
          select id into _id from novel n where n.link = _link;
        end if;

        if _ori_title <> _title or _ori_thumbnail <> _thumbnail or _is_end <> _ori_is_end then 
          UPDATE "novel" SET 
            "title" = _title, 
            "thumbnail" = _thumbnail,
            "is_end" = _is_end
            WHERE "link" = _link;
        end if;
          
        INSERT INTO "novel-info"("createdAt", "updatedAt", "view", "good", "book", "novelId") 
        VALUES 
        (DEFAULT, DEFAULT, _view, _good, _book, _id);
        
      end $$;
      """
    )
    self.conn.commit()

    cur.close()

  def update(self, result: Result):
    cur = self.conn.cursor()

    cur.execute(
      """
      UPDATE "novel" SET 
        "age_limit" = %s,
        "author" = %s
      WHERE "link" = %s;
      """,
      (result.age_limit, result.author, result.link)
    )
    self.conn.commit()

    cur.close()

  def renewal(self):
    cur = self.conn.cursor()

    cur.execute("select link from novel")
    self.conn.commit()
    result = [x[0] for x in cur.fetchall()]
    
    cur.close()

    return result


  def close(self):
    self.conn.close()
  

async def main():
  db = DB()
  novel = NovelStatic()

  for i in db.renewal():
    print(i)
    db.update(await novel.search(i))

  db.close()
  
if __name__ == '__main__':
  asyncio.run(main())