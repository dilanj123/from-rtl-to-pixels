#!/usr/bin/env python3
import argparse, json
from pathlib import Path

def domain(value):
    if value == '<async>': return 'async'
    if isinstance(value, str) and value.startswith('posedge '): return 'clock'
    return 'other'

def path_summary(path, kind):
    seg = path.get('path', [])
    anns = []
    for item in seg: anns.extend(item.get('sources', []))
    def delay(types): return sum(float(x.get('delay', 0)) for x in seg if x.get('type') in types)
    first = seg[0].get('from') if seg else None
    last = seg[-1].get('to') if seg else None
    return {'kind':kind,'from':path.get('from'),'to':path.get('to'),'from_domain':domain(path.get('from')),'to_domain':domain(path.get('to')),'source':first,'sink':last,'total_delay_ns':sum(float(x.get('delay',0)) for x in seg),'clk_to_q_delay_ns':delay({'clk-to-q'}),'logic_delay_ns':delay({'logic'}),'routing_delay_ns':delay({'routing'}),'setup_delay_ns':delay({'setup'}),'source_annotations':list(dict.fromkeys(anns)),'raw_path':path}

def main():
    p=argparse.ArgumentParser()
    for n in ('dimensions','device','package','speed','seed','yosys-stat','report','log','output'): p.add_argument('--'+n,required=True)
    p.add_argument('--target-mhz',required=True,type=float); p.add_argument('--architecture',required=True)
    a=p.parse_args(); stat=json.load(open(a.yosys_stat)); rep=json.load(open(a.report)); log=Path(a.log).read_text(errors='replace')
    cells={}
    def walk(x):
        if isinstance(x,dict):
            if isinstance(x.get('num_cells_by_type'),dict): cells.update(x['num_cells_by_type'])
            for v in x.values(): walk(v)
        elif isinstance(x,list):
            for v in x: walk(v)
    walk(stat)
    util=rep.get('utilization',rep.get('utilisation',{})); clocks=[{'clock':n,'constraint_mhz':v.get('constraint'),'achieved_mhz':v.get('achieved')} for n,v in rep.get('fmax',{}).items() if isinstance(v,dict)]
    paths=rep.get('critical_paths',[]); sync=[]; async_clock=[]; clock=None
    if rep.get('fmax'):
        clock=next(iter(rep['fmax']))
        sync=[x for x in paths if x.get('from')==f'posedge {clock}' and x.get('to')==f'posedge {clock}']
        async_clock=[x for x in paths if x.get('from')=='<async>' and x.get('to')==f'posedge {clock}']
    primary=path_summary(max(sync,key=lambda x:sum(float(y.get('delay',0)) for y in x.get('path',[]))),'clock_to_clock') if sync else None
    async_summary=path_summary(max(async_clock,key=lambda x:sum(float(y.get('delay',0)) for y in x.get('path',[]))),'async_to_clock') if async_clock else None
    out={'architecture':a.architecture,'dimensions':a.dimensions,'device':a.device,'package':a.package,'speed_grade':a.speed,'seed':int(a.seed),'target_mhz':a.target_mhz,'yosys_mapped_cells':cells,'nextpnr_utilization':util,'clocks':clocks,'timing_clean':bool(clocks) and all(c.get('achieved_mhz') is not None and c['achieved_mhz']>=a.target_mhz for c in clocks),'critical_path_kind':'clock_to_clock' if primary else None,'critical_path':primary,'synchronous_critical_path':primary,'async_to_clock_critical_path':async_summary,'clock_to_async_critical_path':None,'async_to_async_critical_path':None,'critical_path_log_lines':[x for x in log.splitlines() if 'critical path' in x.lower() or 'Max frequency for clock' in x],'raw_report':rep}
    json.dump(out,open(a.output,'w'),indent=2); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
