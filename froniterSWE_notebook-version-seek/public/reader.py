from typing import Protocol
class Reader(Protocol):
    size: int
    def read_at(self,offset:int,length:int)->bytes: ...
