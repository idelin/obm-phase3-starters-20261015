from pathlib import Path
import hashlib,os,tempfile
class Payloads:
 def __init__(self,path):self.root=Path(path);self.root.mkdir(parents=True,exist_ok=True);self.pending={}
 def put(self,data):
  h=hashlib.sha256(data).hexdigest();self.pending[h]=data;return h
 def flush(self):
  for data in self.pending.values():self.write(data)
  self.pending.clear()
 def write(self,data):
  h=hashlib.sha256(data).hexdigest();dest=self.root/(h+'.bin')
  if not dest.exists():
   fd,tmp=tempfile.mkstemp(prefix='.stage-',dir=self.root)
   try:
    with os.fdopen(fd,'wb')as f:f.write(data);f.flush();os.fsync(f.fileno())
    os.replace(tmp,dest)
    d=os.open(self.root,os.O_RDONLY);os.fsync(d);os.close(d)
   finally:
    if os.path.exists(tmp):os.unlink(tmp)
  return h
 def get(self,h):return (self.root/(h+'.bin')).read_bytes()
 def collect(self,keep):
  for p in self.root.iterdir():
   if p.name.startswith('.stage-')or(p.suffix=='.bin'and p.stem not in keep):p.unlink()
