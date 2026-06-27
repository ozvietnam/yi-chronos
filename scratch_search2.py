import sqlite3
c = sqlite3.connect('data/yi_wiki/wiki.sqlite3')

# Romanized search
for kw in ['Tham Lang','tham lang','貪','狼']:
    print('### kw=',repr(kw))
    for cid in ['tuvi-toan-thu-lht-zh','tuvi-dao-tang-zh','tuvidauso-zh-q1','tuvidauso-zh-q1q3q4']:
        rows = list(c.execute('SELECT page_start FROM passages WHERE corpus_id=? AND raw_text LIKE ?',(cid,'%'+kw+'%')))
        print('  ',cid, len(rows))
