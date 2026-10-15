from math import gcd,prod

def valid(r):
 if type(r)is not dict or set(r)!={'source','target','source_edges','target_edges','domains','reference','weights','budgets','min_correct'}:raise ValueError()
 def names(v):return type(v)is list and all(isinstance(x,str)and 1<=len(x)<=64 for x in v)and len(set(v))==len(v)
 a,b=r['source'],r['target']
 if not names(a)or not names(b)or not 1<=len(a)<=80 or not len(a)<=len(b)<=160:raise ValueError()
 for key,nodes in [('source_edges',a),('target_edges',b)]:
  es=r[key]
  if type(es)is not list or len(es)>10000:raise ValueError()
  seen=set()
  for e in es:
   if type(e)is not list or len(e)!=2 or any(x not in nodes for x in e)or e[0]==e[1]:raise ValueError()
   z=tuple(sorted(e))
   if z in seen:raise ValueError()
   seen.add(z)
 for k in ('domains','reference','weights'):
  if type(r[k])is not dict or set(r[k])!=set(a):raise ValueError()
 for u in a:
  if not names(r['domains'][u])or not 1<=len(r['domains'][u])<=8 or any(x not in b for x in r['domains'][u]):raise ValueError()
  if r['reference'][u]not in b or type(r['weights'][u])is not int or not 1<=r['weights'][u]<=10**6:raise ValueError()
 if len(set(r['reference'].values()))!=len(a):raise ValueError()
 if prod(len(r['domains'][u])for u in a)>2000000:raise ValueError()
 if type(r['budgets'])is not list or not 1<=len(r['budgets'])<=32 or any(type(v)is not int or not 0<=v<=80*10**6 for v in r['budgets']):raise ValueError()
 if type(r['min_correct'])is not int or not 0<=r['min_correct']<=len(a):raise ValueError()

