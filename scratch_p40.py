import sqlite3
c = sqlite3.connect('data/yi_wiki/wiki.sqlite3')
t = c.execute("SELECT raw_text FROM passages WHERE corpus_id='tuvi-toan-thu-lht-zh' AND page_start=40").fetchone()[0]
i = t.find('火')
# find the Hoa Tham格 Chinese
import re
print('=== p40 火贪 cách (Chinese around) ===')
j = t.find('火贪') if '火贪' in t else t.find('火遇')
if j<0: j=t.find('Luận tham lang ngộ hỏa')
print(t[max(0,j-40):j+260])
