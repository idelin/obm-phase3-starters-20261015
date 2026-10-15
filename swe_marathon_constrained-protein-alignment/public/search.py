from fractions import Fraction

def solve(r):
 try:
  source=sorted(r['source']);used=set();mapping={}
  for u in source:
   choices=sorted(r['domains'][u],key=lambda v:(v!=r['reference'][u],v))
   v=next((v for v in choices if v not in used),None)
   if v is None:return {'results':[{'budget':b,'error':'UNSAT'}for b in r['budgets']]}
   used.add(v);mapping[u]=v
  se={frozenset(e)for e in r['source_edges']};te={frozenset(e)for e in r['target_edges']}
  conserved=sum(frozenset(mapping[u]for u in e)in te for e in se)
  induced=sum(e<=used for e in te);den=len(se)+induced-conserved
  score=Fraction(conserved,den)if den else Fraction(1)
  cost=sum(r['weights'][u]for u in source if mapping[u]!=r['reference'][u]);correct=sum(mapping[u]==r['reference'][u]for u in source)
  return {'results':[{'budget':b,'mapping':[[u,mapping[u]]for u in source],'score':[score.numerator,score.denominator],'cost':cost,'correct':correct,'conserved':conserved,'induced':induced}if cost<=b and correct>=r['min_correct']else {'budget':b,'error':'UNSAT'}for b in r['budgets']]}
 except (ValueError,TypeError,KeyError):return {'error':'BAD_INPUT'}
