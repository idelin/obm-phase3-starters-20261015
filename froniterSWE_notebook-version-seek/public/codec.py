import pickle,zlib
from versions import snapshots

def build(versions):return zlib.compress(pickle.dumps(snapshots(versions),protocol=5),6)

def read(reader,revision,name,offset,length):
    views=pickle.loads(zlib.decompress(reader.read_at(0,reader.size)))
    if revision not in views:return {'error':'VERSION'}
    if name not in views[revision]:return {'error':'NOT_FOUND'}
    data=views[revision][name]
    if offset+length>len(data):return {'error':'RANGE'}
    return {'data':data[offset:offset+length]}
