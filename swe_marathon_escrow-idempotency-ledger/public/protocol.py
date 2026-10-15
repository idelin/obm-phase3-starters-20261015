import re
FIELDS={'init':{'wallets','merchants','ttl'},'authorize':{'merchant','token','id','wallet','amount','expires'},'capture':{'merchant','token','id','amount','final'},'cancel':{'merchant','token','id'},'refund':{'merchant','token','id','refund','amount'},'snapshot':set(),'settle':{'merchant','token','actions'},'claim':{'worker','limit','lease'},'ack':{'worker','event','attempt','success'},'journal':{'after','limit'}}
def integer(v,a,b):return type(v)is int and a<=v<=b
def ident(v):return isinstance(v,str)and re.fullmatch('[a-z][a-z0-9_]{0,31}',v)is not None
def action(r):
 fields={'capture':{'op','id','amount','final'},'cancel':{'op','id'},'refund':{'op','id','refund','amount'}}
 if type(r)is not dict or type(r.get('op'))is not str or r['op']not in fields or set(r)!=fields[r['op']]:raise ValueError()
 for k in ('id','refund'):
  if k in r and not ident(r[k]):raise ValueError()
 if 'amount'in r and not integer(r['amount'],1,10**12):raise ValueError()
 if r['op']=='capture'and type(r['final'])is not bool:raise ValueError()
def validate(r):
 if type(r)is not dict or type(r.get('op'))is not str or r['op']not in FIELDS or set(r)!=(FIELDS[r['op']]|{'op','now'})or not integer(r['now'],0,10**12):raise ValueError()
 op=r['op']
 for k in ('merchant','token','id','wallet','refund','worker'):
  if k in r and not ident(r[k]):raise ValueError()
 if 'amount'in r and not integer(r['amount'],1,10**12):raise ValueError()
 if op=='authorize'and not integer(r['expires'],0,10**12):raise ValueError()
 if op=='capture'and type(r['final'])is not bool:raise ValueError()
 if op=='settle':
  if type(r['actions'])is not list or not 1<=len(r['actions'])<=1000:raise ValueError()
  for a in r['actions']:action(a)
 if op=='init':
  if type(r['wallets'])is not dict or not 1<=len(r['wallets'])<=100000 or any(not ident(k)or not integer(v,0,10**12)for k,v in r['wallets'].items()):raise ValueError()
  if type(r['merchants'])is not list or not 1<=len(r['merchants'])<=10000 or any(not ident(k)for k in r['merchants'])or len(set(r['merchants']))!=len(r['merchants'])or not integer(r['ttl'],1,10**6):raise ValueError()
 if op in('claim','journal')and not integer(r['limit'],1,1000):raise ValueError()
 if op=='claim'and not integer(r['lease'],1,1000000):raise ValueError()
 if op=='journal'and not integer(r['after'],0,10**12):raise ValueError()
 if op=='ack'and(not integer(r['event'],1,10**12)or not integer(r['attempt'],1,10**12)or type(r['success'])is not bool):raise ValueError()
