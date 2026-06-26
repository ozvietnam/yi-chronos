import sqlite3, time

DB = "data/yi_wiki/wiki.sqlite3"
CORPUS = "mai-hoa-dich-so-q1q2"

conn = sqlite3.connect(DB, timeout=60)
conn.execute("PRAGMA busy_timeout=60000;")
cur = conn.cursor()

before = cur.execute(
    "SELECT COUNT(*) FROM chunks_v2 WHERE book_corpus_id=?", (CORPUS,)
).fetchone()[0]

cur.execute(
    """
    INSERT INTO chunks_v2 (book_corpus_id, author_id, page_start, page_end, text, legacy_passage_id, is_canonical, created_at)
      SELECT corpus_id, author_id, page_start, page_end, raw_text, passage_id, 1, strftime('%s','now')
      FROM passages WHERE corpus_id=?
      AND passage_id NOT IN (SELECT legacy_passage_id FROM chunks_v2
                             WHERE book_corpus_id=? AND legacy_passage_id IS NOT NULL)
    """,
    (CORPUS, CORPUS),
)
conn.commit()

after = cur.execute(
    "SELECT COUNT(*) FROM chunks_v2 WHERE book_corpus_id=?", (CORPUS,)
).fetchone()[0]

print(f"chunks before={before} after={after} inserted={after-before}")
conn.close()
