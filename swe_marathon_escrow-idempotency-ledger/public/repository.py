import sqlite3,json
SCHEMA='''
CREATE TABLE IF NOT EXISTS meta(id INTEGER PRIMARY KEY CHECK(id=1),clock INTEGER,ttl INTEGER);
INSERT OR IGNORE INTO meta VALUES(1,0,NULL);
CREATE TABLE IF NOT EXISTS wallets(id TEXT PRIMARY KEY,balance INTEGER,reserved INTEGER);
CREATE TABLE IF NOT EXISTS merchants(id TEXT PRIMARY KEY,balance INTEGER);
CREATE TABLE IF NOT EXISTS intents(id TEXT PRIMARY KEY,merchant TEXT,wallet TEXT,amount INTEGER,remaining INTEGER,captured INTEGER,refunded INTEGER,expires INTEGER,status TEXT);
CREATE INDEX IF NOT EXISTS intents_expiry ON intents(status,expires,id);
CREATE TABLE IF NOT EXISTS refunds(id TEXT PRIMARY KEY,intent TEXT,merchant TEXT,amount INTEGER);
CREATE TABLE IF NOT EXISTS cache(merchant TEXT,token TEXT,expires INTEGER,request TEXT,response TEXT,PRIMARY KEY(merchant,token));
CREATE INDEX IF NOT EXISTS cache_expiry ON cache(expires);
CREATE TABLE IF NOT EXISTS ledger(seq INTEGER PRIMARY KEY,kind TEXT,id TEXT,wallet TEXT,merchant TEXT,amount INTEGER);
CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY,kind TEXT,body TEXT,state TEXT,next_at INTEGER,worker TEXT,attempt INTEGER,until INTEGER);
CREATE INDEX IF NOT EXISTS events_ready ON events(state,next_at,seq);
CREATE INDEX IF NOT EXISTS events_lease ON events(state,until,seq);
'''
def connect(path):
 db=sqlite3.connect(path,timeout=60,isolation_level=None);db.row_factory=sqlite3.Row
 db.execute('PRAGMA journal_mode=WAL');db.execute('PRAGMA synchronous=FULL');db.executescript(SCHEMA);return db
def view(row):return dict(row)
def emit(db,kind,body,now):db.execute('INSERT INTO events(kind,body,state,next_at,worker,attempt,until)VALUES(?,?,\'pending\',?,NULL,0,NULL)',(kind,json.dumps(body,sort_keys=True,separators=(',',':')),now))
def advance(db,now):
 db.execute('UPDATE meta SET clock=?',(now,))
 for p in db.execute("SELECT *FROM intents WHERE status='open'AND expires<=?ORDER BY id",(now,)).fetchall():
  db.execute('UPDATE wallets SET reserved=reserved-?WHERE id=?',(p['remaining'],p['wallet']))
  db.execute("UPDATE intents SET remaining=0,status='expired'WHERE id=?",(p['id'],));p=dict(p);p.update(remaining=0,status='expired');emit(db,'expired',p,now)
 db.execute('DELETE FROM cache WHERE expires<=?',(now,))
