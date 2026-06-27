import sqlite3
c = sqlite3.connect('data/yi_wiki/wiki.sqlite3')
t = c.execute("SELECT raw_text FROM passages WHERE corpus_id='tuvi-toan-thu-lht-zh' AND page_start=64").fetchone()[0]
for kw in ['贪狼化禄','化禄居四墓','卯酉','贪狼属木, 化桃花杀','贪狼入庙长耸']:
    j=t.find(kw)
    if j>=0:
        print('### find',kw)
        print(t[j:j+200])
        print()
