import random,json
def corpus(seed):
 rng=random.Random(seed);alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';words=[''.join(rng.choice(alphabet) for _ in range(64)) for _ in range(2048)];files={}
 for i in range(4):
  text=' '.join(rng.choice(words) for _ in range(32768));files[f'n{i}.ipynb']=json.dumps({'cells':[{'cell_type':'raw','metadata':{},'source':[text]}],'metadata':{},'nbformat':4,'nbformat_minor':5},separators=(',',':')).encode()
 return files
