import copy
from validation import valid
from search import solve

def run(request):
 if type(request)is not dict or 'updates'not in request:raise ValueError()
 state={k:copy.deepcopy(v)for k,v in request.items()if k!='updates'}
 valid(state)
 edits=request['updates']
 if type(edits)is not list or len(edits)>128:raise ValueError()
 for edit in edits:
  if type(edit)is not dict or set(edit)!={'graph','edge','present'}or edit['graph']not in('source','target')or type(edit['present'])is not bool:raise ValueError()
  if type(edit['edge'])is not list or len(edit['edge'])!=2 or edit['edge'][0]==edit['edge'][1]or any(v not in state[edit['graph']]for v in edit['edge']):raise ValueError()
 snapshots=[solve(state)]
 for edit in edits:
  key=edit['graph']+'_edges';edges={frozenset(e)for e in state[key]};edge=frozenset(edit['edge'])
  if edit['present']:edges.add(edge)
  else:edges.discard(edge)
  state[key]=[sorted(e)for e in edges]
  snapshots.append(solve(state))
 return {'snapshots':snapshots}

def apply(request):
 try:return run(request)
 except (ValueError,TypeError,KeyError):return {'error':'BAD_INPUT'}
