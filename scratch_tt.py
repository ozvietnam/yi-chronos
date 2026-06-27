import sqlite3
c = sqlite3.connect('data/yi_wiki/wiki.sqlite3')
for p,t in c.execute("SELECT page_start,raw_text FROM passages WHERE corpus_id='tuvi-toan-thu-lht-zh' AND raw_text LIKE '%Tham Lang%'"):
    # show contexts where Tham Lang is the SUBJECT
    print('--- p',p,'len',len(t),'---')
    # print first 200 + find lines
    import re
    for line in t.split('\n'):
        if 'Tham Lang' in line or 'tham lang' in line.lower():
            print('  >',line.strip()[:160])
