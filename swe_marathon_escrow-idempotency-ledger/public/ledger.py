from repository import emit

def fail(c):return {'error':c}
def post(db,kind,i,w,m,amount):
 db.execute('UPDATE wallets SET balance=balance-?WHERE id=?',(amount,w));db.execute('UPDATE merchants SET balance=balance+?WHERE id=?',(amount,m));db.execute('INSERT INTO ledger(kind,id,wallet,merchant,amount)VALUES(?,?,?,?,?)',(kind,i,w,m,amount))
def execute(db,m,r,now):
 op=r['op']
 if op=='authorize':
  if db.execute('SELECT 1 FROM intents WHERE id=?',(r['id'],)).fetchone():return fail('INTENT_EXISTS')
  w=db.execute('SELECT *FROM wallets WHERE id=?',(r['wallet'],)).fetchone()
  if w is None:return fail('NO_WALLET')
  if r['expires']<=now:return fail('BAD_EXPIRY')
  if r['amount']>w['balance']-w['reserved']:return fail('INSUFFICIENT_FUNDS')
  db.execute('INSERT INTO intents VALUES(?,?,?,?,?,0,0,?,\'open\')',(r['id'],m,r['wallet'],r['amount'],r['amount'],r['expires']));db.execute('UPDATE wallets SET reserved=reserved+?WHERE id=?',(r['amount'],r['wallet']))
  result=dict(db.execute('SELECT *FROM intents WHERE id=?',(r['id'],)).fetchone());emit(db,'authorize',result,now);return result
 p=db.execute('SELECT *FROM intents WHERE id=?AND merchant=?',(r['id'],m)).fetchone()
 if p is None:return fail('NO_INTENT')
 if op=='capture':
  if p['status']!='open':return fail('UNEXPECTED_STATE')
  if r['amount']>p['remaining']:return fail('AMOUNT_TOO_LARGE')
  remaining=p['remaining']-r['amount'];closed=r['final']or remaining==0
  released=r['amount']
  db.execute('UPDATE wallets SET reserved=reserved-?WHERE id=?',(released,p['wallet']))
  db.execute('UPDATE intents SET captured=captured+?,remaining=?,status=?WHERE id=?',(r['amount'],0 if closed else remaining,'closed'if closed else'open',p['id']))
  post(db,'capture',p['id'],p['wallet'],m,r['amount'])
 elif op=='cancel':
  if p['status']!='open':return fail('UNEXPECTED_STATE')
  db.execute('UPDATE wallets SET reserved=reserved-?WHERE id=?',(p['remaining'],p['wallet']));db.execute("UPDATE intents SET remaining=0,status='canceled'WHERE id=?",(p['id'],))
 elif op=='refund':
  if db.execute('SELECT 1 FROM refunds WHERE id=?',(r['refund'],)).fetchone():return fail('REFUND_EXISTS')
  if r['amount']>p['amount']-p['refunded']:return fail('AMOUNT_TOO_LARGE')
  db.execute('UPDATE intents SET refunded=refunded+?WHERE id=?',(r['amount'],p['id']));post(db,'refund',r['refund'],p['wallet'],m,-r['amount']);db.execute('INSERT INTO refunds VALUES(?,?,?,?)',(r['refund'],p['id'],m,r['amount']))
  result={'id':r['refund'],'intent':p['id'],'merchant':m,'amount':r['amount']};emit(db,'refund',result,now);return result
 result=dict(db.execute('SELECT *FROM intents WHERE id=?',(p['id'],)).fetchone());emit(db,op,result,now);return result
