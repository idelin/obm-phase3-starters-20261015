import json
from repository import advance
from protocol import validate
from ledger import execute
from outbox import apply as delivery

def apply(db,r):
 validate(r);op=r['op'];meta=db.execute('SELECT *FROM meta').fetchone();now=r['now']
 if now<meta['clock']:return {'error':'CLOCK_REGRESSION'}
 if op=='init':
  if meta['ttl']is not None:return {'error':'ALREADY_INITIALIZED'}
  db.execute('UPDATE meta SET clock=?,ttl=?',(now,r['ttl']));db.executemany('INSERT INTO wallets VALUES(?,?,0)',r['wallets'].items());db.executemany('INSERT INTO merchants VALUES(?,0)',((m,)for m in r['merchants']));return {'ok':True}
 if meta['ttl']is None:return {'error':'NOT_INITIALIZED'}
 if op not in ('snapshot','journal','claim','ack'):
  early=db.execute('SELECT *FROM cache WHERE merchant=?AND token=?',(r['merchant'],r['token'])).fetchone()
  f=json.dumps({k:v for k,v in r.items()if k not in('token','now')},sort_keys=True,separators=(',',':'))
  if early and early['expires']>=now and early['request']==f:return json.loads(early['response'])
 advance(db,now)
 if op=='snapshot':
  return {'now':now,'wallets':{w['id']:{'balance':w['balance'],'reserved':w['reserved'],'available':w['balance']-w['reserved']}for w in db.execute('SELECT *FROM wallets ORDER BY id')},'merchants':{m['id']:m['balance']for m in db.execute('SELECT *FROM merchants ORDER BY id')},'intents':[dict(p)for p in db.execute('SELECT *FROM intents ORDER BY id')],'refunds':[dict(p)for p in db.execute('SELECT *FROM refunds ORDER BY id')],'ledger':[dict(p)for p in db.execute('SELECT *FROM ledger ORDER BY seq')]}
 if op=='journal':
  rows=[dict(x)for x in db.execute('SELECT *FROM ledger WHERE seq>?ORDER BY seq LIMIT ?',(r['after'],r['limit']+1))];more=len(rows)>r['limit'];rows=rows[:r['limit']];return {'entries':rows,'next':rows[-1]['seq']if more else None}
 if op in('claim','ack'):return delivery(db,r)
 m=r['merchant'];token=r['token']
 if not db.execute('SELECT 1 FROM merchants WHERE id=?',(m,)).fetchone():return {'error':'NO_MERCHANT'}
 f=json.dumps({k:v for k,v in r.items()if k not in('token','now')},sort_keys=True,separators=(',',':'));cached=db.execute('SELECT *FROM cache WHERE merchant=?AND token=?',(m,token)).fetchone()
 if cached:return json.loads(cached['response'])if cached['request']==f else {'error':'IDEMPOTENCY_CONFLICT'}
 if op=='settle':
  db.execute('SAVEPOINT batch');results=[]
  for i,action in enumerate(r['actions']):
   result=execute(db,m,action,now)
   if 'error'in result:
    result={'error':'BATCH_FAILED','index':i,'cause':result['error']};break
   results.append(result)
  else:result={'results':results}
  db.execute('RELEASE batch')
 else:result=execute(db,m,r,now)
 db.execute('INSERT INTO cache VALUES(?,?,?,?,?)',(m,token,now+meta['ttl'],f,json.dumps(result,sort_keys=True,separators=(',',':'))));return result
