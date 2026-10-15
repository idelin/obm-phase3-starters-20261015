import pickle,zlib

def build(files):
    return zlib.compress(pickle.dumps(files,protocol=5),6)

def read(reader,name,offset,length):
    files=pickle.loads(zlib.decompress(reader.read_at(0,reader.size)))
    if name not in files:return {'error':'NOT_FOUND'}
    data=files[name]
    if offset+length>len(data):return {'error':'RANGE'}
    return {'data':data[offset:offset+length]}
