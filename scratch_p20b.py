import sqlite3
c = sqlite3.connect('data/yi_wiki/wiki.sqlite3')
t = c.execute("SELECT raw_text FROM passages WHERE corpus_id='tuvi-toan-thu-lht-zh' AND page_start=20").fetchone()[0]
i = t.find('希夷先生曰')
print('=== Hi Di tien sinh (Chinese) ===')
print(t[i:i+1400])
