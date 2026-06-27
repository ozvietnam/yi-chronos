import sqlite3
c = sqlite3.connect('data/yi_wiki/wiki.sqlite3')
t = c.execute("SELECT raw_text FROM passages WHERE corpus_id='tuvi-toan-thu-lht-zh' AND page_start=20").fetchone()[0]
# find the Tham Lang section
i = t.find('Vấn tham lang')
print(t[i:i+2600])
