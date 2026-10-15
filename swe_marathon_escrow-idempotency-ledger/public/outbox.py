import json

def apply(db,r):
 now=r['now']
 if r['op']=='claim':
  rows=db.execute("SELECT *FROM events WHERE(state='pending'AND next_at<=?)OR(state='leased'AND until<=?)ORDER BY seq LIMIT ?",(now,now,r['limit'])).fetchall();items=[]
  for row in rows:
   a=row['attempt']+1;until=now+r['lease']
   db.execute("UPDATE events SET state='leased',worker=?,attempt=?,until=?WHERE seq=?",(r['worker'],a,until,row['seq']))
   items.append({'event':row['seq'],'kind':row['kind'],'body':json.loads(row['body']),'attempt':a,'until':until})
  return {'events':items}
 e=db.execute('SELECT *FROM events WHERE seq=?',(r['event'],)).fetchone()
 if e is None:return {'error':'NO_EVENT'}
 same=e['worker']==r['worker']
 if e['state']=='done'and same and r['success']:return {'ok':True}
 if not same or e['state']!='leased':return {'error':'STALE_LEASE'}
 if r['success']:db.execute("UPDATE events SET state='done'WHERE seq=?",(e['seq'],))
 else:db.execute("UPDATE events SET state='pending',next_at=?,until=NULL,worker=NULL WHERE seq=?",(now+min(60,2**min(e['attempt']-1,6)),e['seq']))
 return {'ok':True}
