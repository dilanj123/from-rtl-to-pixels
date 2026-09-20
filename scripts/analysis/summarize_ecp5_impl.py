#!/usr/bin/env python3
import argparse,json,re
from pathlib import Path
p=argparse.ArgumentParser()
for n in ('dimensions','device','package','speed','seed','yosys-stat','report','log','output'): p.add_argument('--'+n,required=True)
p.add_argument('--target-mhz',required=True,type=float)
a=p.parse_args(); stat=json.load(open(a.yosys_stat)); rep=json.load(open(a.report)); log=Path(a.log).read_text(errors='replace')
cells={}
def walk(x):
 if isinstance(x,dict):
  if isinstance(x.get('num_cells_by_type'),dict): cells.update(x['num_cells_by_type'])
  for v in x.values(): walk(v)
 elif isinstance(x,list):
  for v in x: walk(v)
walk(stat)
util=rep.get('utilization',rep.get('utilisation',{}))
clocks=[{'clock':n,'constraint_mhz':v.get('constraint'),'achieved_mhz':v.get('achieved')} for n,v in rep.get('fmax',{}).items() if isinstance(v,dict)]
if not clocks:
 for line in re.findall(r'Max frequency for clock[^\n]*',log):
  m=re.search(r"clock '([^']+)'.*?([0-9]+(?:\.[0-9]+)?) MHz",line)
  if m: clocks.append({'clock':m.group(1),'achieved_mhz':float(m.group(2)),'raw':line})
verdicts=[c.get('achieved_mhz') is not None and c['achieved_mhz']>=a.target_mhz for c in clocks]
def domain(x):
 return 'async' if x=='<async>' else ('clock' if isinstance(x,str) and x.startswith('posedge ') else 'other')
def summarize(path,kind):
 seg=path.get('path',[]); anns=[]
 for x in seg: anns += x.get('sources',[])
 return {'kind':kind,'from_domain':domain(path.get('from')),'to_domain':domain(path.get('to')),
  'source':seg[0].get('from') if seg else None,'sink':seg[-1].get('to') if seg else None,
  'total_delay_ns':sum(float(x.get('delay',0)) for x in seg),
  'clk_to_q_delay_ns':sum(float(x.get('delay',0)) for x in seg if x.get('type')=='clk-to-q'),
  'logic_delay_ns':sum(float(x.get('delay',0)) for x in seg if x.get('type')=='logic'),
  'routing_delay_ns':sum(float(x.get('delay',0)) for x in seg if x.get('type')=='routing'),
  'setup_delay_ns':sum(float(x.get('delay',0)) for x in seg if x.get('type')=='setup'),
  'source_annotations':list(dict.fromkeys(anns)),'raw_path':path}
paths=rep.get('critical_paths',[])
clock=next(iter(rep.get('fmax',{})),None)
sync=[x for x in paths if clock and x.get('from')==f'posedge {clock}' and x.get('to')==f'posedge {clock}']
asyncp=[x for x in paths if x.get('from')=='<async>' and clock and x.get('to')==f'posedge {clock}']
primary=summarize(max(sync,key=lambda x:sum(float(y.get('delay',0)) for y in x.get('path',[]))),'clock_to_clock') if sync else None
async_summary=summarize(max(asyncp,key=lambda x:sum(float(y.get('delay',0)) for y in x.get('path',[]))),'async_to_clock') if asyncp else None
out={'architecture':'A / compact','dimensions':a.dimensions,'device':a.device,'package':a.package,'speed_grade':a.speed,'seed':int(a.seed),'target_mhz':a.target_mhz,'yosys_mapped_cells':cells,'nextpnr_utilization':util,'clocks':clocks,'timing_clean':bool(verdicts) and all(verdicts),'critical_path_kind':'clock_to_clock' if primary else None,'critical_path':primary,'synchronous_critical_path':primary,'async_to_clock_critical_path':async_summary,'clock_to_async_critical_path':None,'async_to_async_critical_path':None,'critical_path_log_lines':[x for x in log.splitlines() if 'critical path' in x.lower() or 'Max frequency for clock' in x],'raw_report':rep}
json.dump(out,open(a.output,'w'),indent=2); print(json.dumps(out,indent=2))
