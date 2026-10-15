import sys,json
from timeline import apply
for line in sys.stdin:
 try:result=apply(json.loads(line))
 except ValueError:result={'error':'BAD_INPUT'}
 print(json.dumps(result,separators=(',',':'),ensure_ascii=False),flush=True)
