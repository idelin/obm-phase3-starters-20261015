from mapping import positions,available

def run(request):
    mapping=list(request['initial']);done=set();schedule=[]
    edges={tuple(e) for e in request['edges']}
    for blocked in request['blocked']:
        if len(done)==len(request['gates']):return {'ticks':len(schedule),'schedule':schedule}
        pos=positions(mapping);ready=available(request['gates'],done);step=[]
        for i in ready:
            u,v=[pos[q] for q in request['gates'][i]]
            if (u,v) in edges and u not in blocked and v not in blocked:
                step=[['gate',i]];done.add(i);break
        schedule.append(step)
    if len(done)==len(request['gates']):return {'ticks':len(schedule),'schedule':schedule}
    return {'error':'DEADLINE'}
