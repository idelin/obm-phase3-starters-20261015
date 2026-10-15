import hashlib,json
from repository import next_seq,visible,usage,retained_hashes
from protocol import validate

def error(c):return {'error':c}
def apply(db,blobs,r):
 validate(r);op=r['op'];meta=db.execute('SELECT * FROM meta').fetchone()
 if op=='init':
  if meta['quota']is not None:return error('ALREADY_INITIALIZED')
  db.execute('UPDATE meta SET quota=?',(r['quota'],));return {'ok':True}
 if meta['quota']is None:return error('NOT_INITIALIZED')
 def current(k):
  v=visible(db,k);return v['id']if v and not v['deleted']else 0
 def commit(k,data,etag):
  h=blobs.put(data);seq=next_seq(db);db.execute('UPDATE meta SET bytes=bytes+?',(len(data),))
  db.execute('INSERT INTO versions VALUES(?,?,0,?,?,?,NULL)',(seq,k,h,len(data),etag));return {'version':seq,'etag':etag}
 def obj(v):return {'version':v['id'],'data':blobs.get(v['hash']).hex(),'etag':v['etag']}
 if op=='stats':return {'bytes':usage(db),'versions':db.execute('SELECT count(*) FROM versions WHERE removed IS NULL').fetchone()[0],'uploads':db.execute('SELECT count(*)FROM uploads').fetchone()[0]}
 if op=='put':
  if r['if_version']is not None and current(r['key'])!=r['if_version']:return error('PRECONDITION')
  b=bytes.fromhex(r['data'])
  if usage(db)+len(b)>meta['quota']:return error('QUOTA')
  return commit(r['key'],b,hashlib.md5(b).hexdigest())
 if op=='begin':
  if db.execute('SELECT 1 FROM uploads WHERE id=? UNION ALL SELECT 1 FROM receipts WHERE upload=?',(r['upload'],r['upload'])).fetchone():return error('UPLOAD_EXISTS')
  db.execute('INSERT INTO uploads VALUES(?,?)',(r['upload'],r['key']));return {'ok':True}
 if op=='part':
  if not db.execute('SELECT 1 FROM uploads WHERE id=?',(r['upload'],)).fetchone():return error('NO_UPLOAD')
  b=bytes.fromhex(r['data']);h=blobs.put(b);e=hashlib.md5(b).hexdigest()
  db.execute('INSERT OR REPLACE INTO parts VALUES(?,?,?,?,?)',(r['upload'],r['number'],h,len(b),e));return {'etag':e}
 if op=='abort':
  if not db.execute('SELECT 1 FROM uploads WHERE id=?',(r['upload'],)).fetchone():return error('NO_UPLOAD')
  db.execute('DELETE FROM uploads WHERE id=?',(r['upload'],));db.execute('DELETE FROM parts WHERE upload=?',(r['upload'],));return {'ok':True}
 if op=='complete':
  f=json.dumps({k:r[k]for k in('parts','if_version')},sort_keys=True,separators=(',',':'))
  done=db.execute('SELECT *FROM receipts WHERE upload=?',(r['upload'],)).fetchone()
  if done:
   response=json.loads(done['response']);v=db.execute('SELECT key FROM versions WHERE id=?',(response['version'],)).fetchone()
   if v and r['if_version']is not None and current(v['key'])!=r['if_version']:return error('PRECONDITION')
   return response
  u=db.execute('SELECT *FROM uploads WHERE id=?',(r['upload'],)).fetchone()
  if not u:return error('NO_UPLOAD')
  nums=[p['number']for p in r['parts']]
  if any(a>=b for a,b in zip(nums,nums[1:])):return error('PART_ORDER')
  parts=[]
  for p in r['parts']:
   v=db.execute('SELECT *FROM parts WHERE upload=?AND number=?',(r['upload'],p['number'])).fetchone()
   if v is None or v['etag']!=p['etag']:return error('INVALID_PART')
   parts.append(v)
  if any(v['size']<4096 for v in parts[:-1]):return error('PART_TOO_SMALL')
  if sum(v['size']for v in parts)>64*1024*1024:return error('OBJECT_TOO_LARGE')
  if r['if_version']is not None and current(u['key'])!=r['if_version']:return error('PRECONDITION')
  if usage(db)+sum(v['size']for v in parts)>meta['quota']:return error('QUOTA')
  b=b''.join(blobs.get(v['hash'])for v in parts);e=hashlib.md5(b''.join(bytes.fromhex(v['etag'])for v in parts)).hexdigest()+'-'+str(len(parts))
  result=commit(u['key'],b,e);db.execute('INSERT INTO receipts VALUES(?,?,?)',(r['upload'],f,json.dumps(result)));db.execute('DELETE FROM uploads WHERE id=?',(r['upload'],));db.execute('DELETE FROM parts WHERE upload=?',(r['upload'],));return result
 if op=='delete':
  if r['version']is None:
   seq=next_seq(db);db.execute('INSERT INTO versions VALUES(?,?,1,NULL,0,NULL,NULL)',(seq,r['key']));return {'version':seq,'deleted':True}
  v=db.execute('SELECT *FROM versions WHERE key=?AND id=?AND removed IS NULL',(r['key'],r['version'])).fetchone()
  if v is None:return error('NO_VERSION')
  db.execute('UPDATE meta SET bytes=bytes-?',(v['size'],));seq=next_seq(db);db.execute('UPDATE versions SET removed=?WHERE id=?',(seq,r['version']));return {'version':r['version'],'deleted':bool(v['deleted'])}
 if op=='get':
  v=visible(db,r['key'])if r['version']is None else db.execute('SELECT *FROM versions WHERE key=?AND id=?AND removed IS NULL',(r['key'],r['version'])).fetchone()
  if v is None:return error('NO_KEY'if r['version']is None else'NO_VERSION')
  return error('DELETE_MARKER')if v['deleted']else obj(v)
 if op=='list':
  out=[]
  for row in db.execute('SELECT DISTINCT key FROM versions ORDER BY key'):
   v=visible(db,row['key'])
   if v and not v['deleted']:out.append({'key':v['key'],'version':v['id'],'etag':v['etag'],'size':v['size']})
  return {'objects':out}
 if op=='scan_open':
  if db.execute('SELECT 1 FROM scans WHERE id=?',(r['scan'],)).fetchone():return error('SCAN_EXISTS')
  if db.execute('SELECT count(*)FROM scans').fetchone()[0]>=32:return error('SCAN_LIMIT')
  db.execute('INSERT INTO scans VALUES(?,?,?)',(r['scan'],r['prefix'],meta['seq']));return {'ok':True}
 if op in ('scan_page','scan_get','scan_close'):
  scan=db.execute('SELECT *FROM scans WHERE id=?',(r['scan'],)).fetchone()
  if scan is None:return error('NO_SCAN')
  if op=='scan_close':db.execute('DELETE FROM scans WHERE id=?',(r['scan'],));return {'ok':True}
  if op=='scan_get':
   v=visible(db,r['key'],scan['seq'])if r['key'].startswith(scan['prefix'])else None
   if v is None or v['deleted']:return error('NO_KEY')
   return obj(v)
  rows=[];limit=r['limit'];after=r['after']
  for row in db.execute('SELECT DISTINCT key FROM versions WHERE key>? AND key>=? ORDER BY key',(after if after is not None else '',scan['prefix'])):
   k=row['key']
   if not k.startswith(scan['prefix']):continue
   v=visible(db,k,scan['seq'])
   if v and not v['deleted']:
    rows.append({'key':k,'version':v['id'],'etag':v['etag'],'size':v['size']})
    if len(rows)>limit:break
  truncated=len(rows)>limit;rows=rows[:limit]
  return {'objects':rows,'next':rows[-1]['key']if truncated else None}
 if op=='vacuum':blobs.collect(retained_hashes(db));return {'ok':True}
