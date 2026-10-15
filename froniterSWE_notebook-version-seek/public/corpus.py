import random,json
def corpus(seed):
 rng=random.Random(seed);alphabet=b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';ops=[]
 for j in range(4):
  text=bytes(rng.choice(alphabet) for _ in range(48000));raw=b'{"cells":[{"cell_type":"raw","metadata":{},"source":["'+text+b'"]}],"metadata":{},"nbformat":4,"nbformat_minor":5}'
  ops.append({'op':'put','name':f'n{j}.ipynb','data':raw})
 versions=[{'id':'v000','parent':None,'ops':ops}]
 for i in range(1,96):
  versions.append({'id':f'v{i:03d}','parent':f'v{(i-1)//2:03d}','ops':[{'op':'splice','name':f'n{i%4}.ipynb','offset':1000+rng.randrange(45000),'delete':rng.randrange(10),'data':bytes(rng.choice(alphabet) for _ in range(5+rng.randrange(30)))}]})
 return versions
