#!/usr/bin/env python3
import csv,json,os,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]; route=root/'scripts/timing/run_arch_a_route.sh'; build=root/'build/impl/arch-a/640x480/route'; rows=[]
def run(f):
 out=build/f'freq-{f}MHz-seed-1'; out.mkdir(parents=True,exist_ok=True)
 r=subprocess.run([str(route),str(f),'1'],capture_output=True,text=True)
 status=out/'status.txt'; route_ok='ROUTE_STATUS=PASS' in status.read_text() if status.exists() else False
 summ=out/'summary.json'; s=json.load(open(summ)) if summ.exists() else {}
 clean=route_ok and bool(s.get('timing_clean')); clocks=s.get('clocks',[]); achieved=clocks[0].get('achieved_mhz') if clocks else None
 rows.append({'target_mhz':f,'seed':1,'route_status':'PASS' if route_ok else 'FAIL','reported_clock':clocks[0].get('clock',clocks[0].get('raw','')) if clocks else '','achieved_mhz':achieved,'timing_status':'PASS' if clean else 'FAIL','log_path':str(out/'nextpnr.log'),'report_path':str(out/'nextpnr-report.json')})
 if not route_ok: raise SystemExit(f'route failure at {f} MHz')
 return clean
# Fixed bracket search; all runs use seed 1 and the same netlist.
for f in [25,50,100,200,400]:
 c=run(f)
 if not c:
  if f==25:
   for low in [10,5]:
    if run(low): break
   else: raise SystemExit('no timing-clean lower bound through 5 MHz')
  break
# establish nearest 5 MHz bracket from tested clean/fail points
clean=[r['target_mhz'] for r in rows if r['timing_status']=='PASS']; fail=[r['target_mhz'] for r in rows if r['timing_status']=='FAIL']
if not fail:
 print('No failing bracket found through 400 MHz.')
else:
 lo=max(clean); hi=min(fail)
 while hi-lo>5:
  mid=((lo+hi)//10)*5
  if mid<=lo: mid=lo+5
  (run(mid) and (globals().__setitem__('lo',mid))) or globals().__setitem__('hi',mid)
# write stable CSV and summary copies
res=root/'results/raw'; res.mkdir(parents=True,exist_ok=True)
with open(res/'arch-a-frequency-search.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
clean=[r for r in rows if r['timing_status']=='PASS']; fail=[r for r in rows if r['timing_status']=='FAIL']
print('highest_clean=',max((r['target_mhz'] for r in clean),default=None)); print('lowest_fail=',min((r['target_mhz'] for r in fail),default=None))
