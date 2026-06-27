import sqlite3
kw = "貪狼"  # 貪狼
c = sqlite3.connect('data/yi_wiki/wiki.sqlite3')
for cid in ['tuvi-toan-thu-lht-zh','tuvi-dao-tang-zh','tuvidauso-zh-q1','tuvidauso-zh-q1q3q4']:
    rows = list(c.execute('SELECT page_start,raw_text FROM passages WHERE corpus_id=? AND raw_text LIKE ?',(cid,'%'+kw+'%')))
    print('===', cid, 'hits:', len(rows))
