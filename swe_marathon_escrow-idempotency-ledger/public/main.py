import sys,json
from pathlib import Path
from repository import connect
from service import apply
path=Path(sys.argv[1]);path.mkdir(parents=True,exist_ok=True);db=connect(path/'ledger.sqlite')
for line in sys.stdin:
 try:
  req=json.loads(line);db.execute('BEGIN IMMEDIATE');result=apply(db,req);db.execute('COMMIT')
 except (ValueError,TypeError,KeyError,IndexError):
  if db.in_transaction:db.execute('ROLLBACK')
  result={'error':'BAD_INPUT'}
 print(json.dumps(result,separators=(',',':')),flush=True)
