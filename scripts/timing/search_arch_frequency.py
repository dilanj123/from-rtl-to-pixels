#!/usr/bin/env python3
import argparse,csv,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def main():
 p=argparse.ArgumentParser(); p.add_argument('--architecture',choices=['compact','pipelined'],required=True); a=p.parse_args()
 rows=[]; cache={}; script=ROOT/'scripts/timing/run_arch_route.sh'; build=ROOT/f'build/impl/arch-{"a" if a.architecture=="compact" else "b"}/640x480'
 def run(f):
  if f in cache:return cache[f]
  out=build/f'route/freq-{f}MHz-seed-1'; r=subprocess.run([str(script),a.architecture,str(f),'1'],capture_output=True,text=True)
  status=(out/'status.txt').read_text() if (out/'status.txt').exists() else ''
  route_ok='ROUTE_STATUS=PASS' in status; summ=json.load(open(out/'summary.json')) if (out/'summary.json').exists() else {}
  clocks=summ.get('clocks',[]); c=clocks[0] if clocks else {}; clean=route_ok and summ.get('timing_clean',False)
  row={'target_mhz':f,'seed':1,'route_status':'PASS' if route_ok else 'FAIL','reported_clock':c.get('clock',''),'achieved_mhz':c.get('achieved_mhz'),'timing_status':'PASS' if clean else 'FAIL','log_path':str(out/'nextpnr.log'),'report_path':str(out/'nextpnr-report.json')}; rows.append(row); cache[f]=clean
  if not route_ok: raise RuntimeError(f'route failure at {f} MHz\n{r.stdout}\n{r.stderr}')
  return clean
 clean=False
 if run(25):
  lo=25; hi=None
  for f in (50,100,200,400):
   if run(f): lo=f
   else: hi=f; break
 else:
  hi=25; lo=None
  for f in (10,5):
   if run(f): lo=f; break
  if lo is None: raise RuntimeError('5 MHz not timing-clean')
 if hi is not None:
  while hi-lo>5:
   mid=int(((lo+hi)/2)//5)*5
   if mid<=lo: mid=lo+5
   if mid>=hi: mid=hi-5
   if run(mid): lo=mid
   else: hi=mid
  result={'highest_clean':lo,'lowest_fail':hi,'bracket_width':hi-lo}
 else: result={'highest_clean':lo,'lowest_fail':None,'bracket_width':None,'open_upper_bound':True}
 out=ROOT/f'build/impl/arch-{"a" if a.architecture=="compact" else "b"}/640x480/frequency-search.csv'; out.parent.mkdir(parents=True,exist_ok=True)
 with open(out,'w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
 print(json.dumps({'architecture':a.architecture,'seed':1,'grid_mhz':5,'tested':rows,**result},indent=2))
if __name__=='__main__': main()
