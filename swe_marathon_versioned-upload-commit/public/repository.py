import sqlite3,json
SCHEMA='''
CREATE TABLE IF NOT EXISTS meta(id INTEGER PRIMARY KEY CHECK(id=1),quota INTEGER,seq INTEGER NOT NULL,bytes INTEGER NOT NULL);
INSERT OR IGNORE INTO meta VALUES(1,NULL,0,0);
CREATE TABLE IF NOT EXISTS versions(id INTEGER PRIMARY KEY,key TEXT NOT NULL,deleted INTEGER NOT NULL,hash TEXT,size INTEGER,etag TEXT,removed INTEGER);
CREATE INDEX IF NOT EXISTS versions_key ON versions(key,id DESC);
CREATE INDEX IF NOT EXISTS versions_removed ON versions(removed,id);
CREATE TABLE IF NOT EXISTS uploads(id TEXT PRIMARY KEY,key TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS parts(upload TEXT,number INTEGER,hash TEXT,size INTEGER,etag TEXT,PRIMARY KEY(upload,number));
CREATE INDEX IF NOT EXISTS parts_hash ON parts(hash);
CREATE TABLE IF NOT EXISTS receipts(upload TEXT PRIMARY KEY,request TEXT NOT NULL,response TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS scans(id TEXT PRIMARY KEY,prefix TEXT NOT NULL,seq INTEGER NOT NULL);
'''
def connect(path):
 db=sqlite3.connect(path,timeout=60,isolation_level=None);db.row_factory=sqlite3.Row
 db.execute('PRAGMA journal_mode=WAL');db.execute('PRAGMA synchronous=FULL');db.executescript(SCHEMA);return db
def next_seq(db):
 db.execute('UPDATE meta SET seq=seq+1 WHERE id=1');return db.execute('SELECT seq FROM meta').fetchone()[0]
def visible(db,key,at=None):
 if at is None:return db.execute('SELECT * FROM versions WHERE key=? AND removed IS NULL ORDER BY id DESC LIMIT 1',(key,)).fetchone()
 return db.execute('SELECT * FROM versions WHERE key=? AND id<=? AND removed IS NULL ORDER BY id DESC LIMIT 1',(key,at)).fetchone()
def usage(db):return db.execute('SELECT bytes FROM meta').fetchone()[0]
def retained_hashes(db):
 keep={x[0]for x in db.execute('SELECT hash FROM parts')}
 keep.update(x[0]for x in db.execute('SELECT hash FROM versions WHERE removed IS NULL AND deleted=0'))
 return keep
