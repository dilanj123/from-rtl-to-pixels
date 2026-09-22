#!/usr/bin/env python3
import argparse,csv,json
p=argparse.ArgumentParser()
for n in ('a-stat','b-stat','a-summary','b-summary','a-search','b-search','a-perf','b-perf','output'): p.add_argument('--'+n,required=True)
a=p.parse_args(); A=json.load(open(a.a_stat)); B=json.load(open(a.b_stat)); AS=json.load(open(a.a_summary)); BS=json.load(open(a.b_summary)); AP=json.load(open(a.a_perf)); BP=json.load(open(a.b_perf))
def cells(x):
 out={}
 def w(v):
  if isinstance(v,dict):
   if isinstance(v.get('num_cells_by_type'),dict): out.update(v['num_cells_by_type'])
   for z in v.values():w(z)
  elif isinstance(v,list):
   for z in v:w(z)
 w(x); return out
ac,bc=cells(A),cells(B)
def search(path):
 rows=list(csv.DictReader(open(path))); clean=[r for r in rows if r['timing_status']=='PASS']; fail=[r for r in rows if r['timing_status']=='FAIL']; return {'tested':rows,'highest_clean':max(int(r['target_mhz']) for r in clean),'lowest_fail':min(int(r['target_mhz']) for r in fail),'bracket_width':min(int(r['target_mhz']) for r in fail)-max(int(r['target_mhz']) for r in clean)}
aq,bq=search(a.a_search),search(a.b_search); keys=sorted(set(ac)|set(bc)); resources={k:{'A':ac.get(k,0),'B':bc.get(k,0),'delta':bc.get(k,0)-ac.get(k,0)} for k in keys}
def path(s): return s.get('synchronous_critical_path')
out={'target':{'dimensions':'640x480','device':'LFE5U-45F','package':'CABGA381','speed':6,'seed':1},'resources':resources,'timing':{'A':aq,'B':bq,'A_clean_summary':AS,'B_clean_summary':BS,'A_path':path(AS),'B_path':path(BS)},'performance':{'A':AP,'B':BP,'latency_delta':BP['first_output_latency_cycles']-AP['first_output_latency_cycles'],'frame_cycles_delta':BP['frame_completion_cycles']-AP['frame_completion_cycles']},'derived':{'A_peak_mpixel_s':aq['highest_clean']/AP['input_ii_max'],'B_peak_mpixel_s':bq['highest_clean']/BP['input_ii_max'],'A_frame_s':aq['highest_clean']*1e6/AP['frame_completion_cycles'],'B_frame_s':bq['highest_clean']*1e6/BP['frame_completion_cycles'],'A_effective_mpixel_s':aq['highest_clean']*AP['accepted_output_count']/AP['frame_completion_cycles'],'B_effective_mpixel_s':bq['highest_clean']*BP['accepted_output_count']/BP['frame_completion_cycles']}}
json.dump(out,open(a.output,'w'),indent=2); print(json.dumps(out,indent=2))
