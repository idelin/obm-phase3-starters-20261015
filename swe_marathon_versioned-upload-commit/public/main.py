import sys,json
from pathlib import Path
from repository import connect
from payloads import Payloads
from service import apply
path=Path(sys.argv[1]);path.mkdir(parents=True,exist_ok=True)
db=connect(path/'metadata.sqlite');blobs=Payloads(path/'payloads')
for line in sys.stdin:
 try:
  req=json.loads(line);db.execute('BEGIN IMMEDIATE');result=apply(db,blobs,req);db.execute('COMMIT');blobs.flush()
 except (ValueError,TypeError,KeyError,IndexError):
  if db.in_transaction:db.execute('ROLLBACK')
  result={'error':'BAD_INPUT'}
 print(json.dumps(result,separators=(',',':'),ensure_ascii=False),flush=True)
