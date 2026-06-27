import sqlite3
c = sqlite3.connect('data/yi_wiki/wiki.sqlite3')
print('===== DAO TANG (貪) =====')
for p,t in c.execute("SELECT page_start,raw_text FROM passages WHERE corpus_id='tuvi-dao-tang-zh' AND raw_text LIKE '%貪%'"):
    print('--- p',p,'---')
    print(t[:900])
    print()
