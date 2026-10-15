import re
FIELDS={'init':{'quota'},'put':{'key','data','if_version'},'begin':{'key','upload'},'part':{'upload','number','data'},'complete':{'upload','parts','if_version'},'abort':{'upload'},'delete':{'key','version'},'get':{'key','version'},'list':set(),'stats':set(),'scan_open':{'scan','prefix'},'scan_page':{'scan','after','limit'},'scan_get':{'scan','key'},'scan_close':{'scan'},'vacuum':set()}
def integer(x,lo,hi):return type(x)is int and lo<=x<=hi
def text(x,empty=False):return isinstance(x,str)and (0 if empty else 1)<=len(x)<=128 and all(ord(c)!=0 and not 0xd800<=ord(c)<=0xdfff for c in x)
def validate(r):
 if type(r)is not dict or type(r.get('op'))is not str or r['op']not in FIELDS or set(r)!=(FIELDS[r['op']]|{'op'}):raise ValueError()
 op=r['op']
 for k in ('key','upload','scan'):
  if k in r and not text(r[k]):raise ValueError()
 if 'prefix'in r and not text(r['prefix'],True):raise ValueError()
 if 'after'in r and r['after']is not None and not text(r['after'],True):raise ValueError()
 for k in ('version','if_version'):
  if k in r and r[k]is not None and not integer(r[k],0,10**15):raise ValueError()
 if 'data'in r and(not isinstance(r['data'],str)or len(r['data'])>2097152 or len(r['data'])%2 or re.fullmatch('[0-9a-f]*',r['data'])is None):raise ValueError()
 if op=='init'and not integer(r['quota'],0,10**12):raise ValueError()
 if op=='part'and not integer(r['number'],1,10000):raise ValueError()
 if op=='scan_page'and not integer(r['limit'],1,1000):raise ValueError()
 if op=='complete':
  if type(r['parts'])is not list or not 1<=len(r['parts'])<=10000:raise ValueError()
  for p in r['parts']:
   if type(p)is not dict or set(p)!={'number','etag'}or not integer(p['number'],1,10000)or not isinstance(p['etag'],str)or re.fullmatch('[0-9a-f]{32}',p['etag'])is None:raise ValueError()
