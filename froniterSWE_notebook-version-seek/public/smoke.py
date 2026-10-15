import codec
class MemoryReader:
    def __init__(self,data):self._data=data;self.size=len(data);self.bytes_read=0
    def read_at(self,offset,length):
        self.bytes_read+=length
        return self._data[offset:offset+length]
source=[{'id':'v0','parent':None,'ops':[{'op':'put','name':'a.ipynb','data':b'{}'}]}]
archive=codec.build(source)
reader=MemoryReader(archive)
print(codec.read(reader,'v0','a.ipynb',0,2))
print({"archive_bytes":len(archive),"read_bytes":reader.bytes_read})
