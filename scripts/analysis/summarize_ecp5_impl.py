#!/usr/bin/env python3
import argparse,json,re
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('--dimensions',required=True); p.add_argument('--device',required=True); p.add_argument('--package',required=True); p.add_argument('--speed',required=True); p.add_argument('--seed',required=True); p.add_argument('--target-mhz',required=True,type=float); p.add_argument('--yosys-stat',required=True); p.add_argument('--report',required=True); p.add_argument('--log',required=True); p.add_argument('--output',required=True)
a=p.parse_args(); stat=json.load(open(a.yosys_stat)); rep=json.load(open(a.report)); log=Path(a.log).read_text(errors='replace')
# Preserve raw Yosys shape and normalize common cell dictionaries.
cells={}
def walk(x):
 if isinstance(x,dict):
  if 'num_cells_by_type' in x and isinstance(x['num_cells_by_type'],dict): cells.update(x['num_cells_by_type'])
  for v in x.values(): walk(v)
 elif isinstance(x,list):
  for v in x: walk(v)
walk(stat)
util=rep.get('utilization',rep.get('utilisation',{}))
clocks=[]
for name,v in rep.get('fmax',{}).items():
 if isinstance(v,dict): clocks.append({'clock':name,'constraint_mhz':v.get('constraint'),'achieved_mhz':v.get('achieved')})
if not clocks:
 for k,v in rep.items():
  if isinstance(v,list) and ('clock' in k.lower() or 'timing' in k.lower()): clocks += [x for x in v if isinstance(x,dict)]
if not clocks:
 for m in re.finditer(r'Max frequency for clock[^\n]*',log):
  line=m.group(0); mm=re.search(r'([0-9]+(?:\.[0-9]+)?)\s*MHz',line); clocks.append({'raw':line,'achieved_mhz':float(mm.group(1)) if mm else None})
if not clocks:
 clocks=[{'raw':x} for x in re.findall(r'Max frequency for clock[^\n]*',log)]
for c in clocks:
 if 'achieved_mhz' not in c:
  for key in ('achieved_mhz','achieved','freq','frequency'):
   if key in c:
    try:c['achieved_mhz']=float(c[key])
    except:pass
verdicts=[(c.get('achieved_mhz') is not None and c.get('achieved_mhz') >= a.target_mhz) for c in clocks]
critical=[]
for i,line in enumerate(log.splitlines()):
 if 'critical path' in line.lower() or 'Max frequency for clock' in line:
  critical.append(line)
paths=rep.get('critical_paths',[])
cp={}
if paths:
 path=max(paths,key=lambda x:sum(float(y.get('delay',0)) for y in x.get('path',[])))
 segs=path.get('path',[])
 cp={'source':segs[0].get('from') if segs else None,'sink':segs[-1].get('to') if segs else None,'total_delay_ns':sum(float(y.get('delay',0)) for y in segs),'logic_delay_ns':sum(float(y.get('delay',0)) for y in segs if y.get('type')=='logic'),'routing_delay_ns':sum(float(y.get('delay',0)) for y in segs if y.get('type')=='routing'),'raw_path':path}
out={'architecture':'A / compact','dimensions':a.dimensions,'device':a.device,'package':a.package,'speed_grade':a.speed,'seed':int(a.seed),'target_mhz':a.target_mhz,'yosys_mapped_cells':cells,'nextpnr_utilization':util,'clocks':clocks,'timing_clean':bool(verdicts) and all(verdicts),'critical_path':cp,'critical_path_raw':critical,'raw_report':rep}
json.dump(out,open(a.output,'w'),indent=2)
print(json.dumps(out,indent=2))
