from mapping import positions,available

def run(request):
    mapping=list(request['initial']);done=set();schedule=[]
    edges={frozenset(e[:2]) for e in request['edges']}
    while len(done)<len(request['gates']):
        pos=positions(mapping);ready=available(request['gates'],done)
        possible=[i for i in ready if frozenset(pos[q] for q in request['gates'][i]) in edges]
        if not possible:return {'error':'UNROUTABLE'}
        i=min(possible);done.add(i);schedule.append([['gate',i]])
    return {'cost':0,'steps':len(schedule),'schedule':schedule}
