import json,sys
from engine import run
for line in sys.stdin:
    try: print(json.dumps(run(json.loads(line)),ensure_ascii=False,allow_nan=False))
    except Exception: print(json.dumps({"error":"UNIMPLEMENTED"}))
