import os, json, numpy as np, cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
W=int(os.environ.get('IMG_WIDTH','640')); H=int(os.environ.get('IMG_HEIGHT','480')); N=W*H

def pixel(i):
 r,c=divmod(i,W); return ((17*r+31*c+3)&255,(43*r+11*c+19)&255,(7*r+53*c+101)&255)
def pack(p): return (p[0]<<16)|(p[1]<<8)|p[2]
async def settle(): await Timer(1,units='ns')
async def apb(d,addr,val=None):
 d.psel.value=1; d.penable.value=0; d.pwrite.value=int(val is not None); d.paddr.value=addr; d.pwdata.value=0 if val is None else val
 await RisingEdge(d.clk); d.penable.value=1; await settle(); out=int(d.prdata.value); assert int(d.pready.value)==1 and int(d.pslverr.value)==0
 await RisingEdge(d.clk); d.psel.value=0; d.penable.value=0; d.pwrite.value=0; return out
@cocotb.test()
async def canonical_performance(d):
 cocotb.start_soon(Clock(d.clk,10,units='ns').start())
 for n,v in [('rst',1),('s_tvalid',0),('m_tready',0),('psel',0),('penable',0),('pwrite',0),('paddr',0),('pwdata',0),('s_tdata',0),('s_tuser',0),('s_tlast',0)]: getattr(d,n).value=v
 await RisingEdge(d.clk); await RisingEdge(d.clk); d.rst.value=0
 await apb(d,0,3); await apb(d,4,0)
 d.m_tready.value=1; input_cycles=[]; output_cycles=[]; outputs=[]; ins=0; cycle=0
 while len(output_cycles)<N:
  if ins<N:
   d.s_tdata.value=pack(pixel(ins)); d.s_tvalid.value=1; d.s_tuser.value=int(ins==0); d.s_tlast.value=int(ins%W==W-1)
  else:
   d.s_tvalid.value=0; d.s_tuser.value=0; d.s_tlast.value=0
  await settle();
  if int(d.s_tvalid.value) and int(d.s_tready.value): input_cycles.append(cycle); ins+=1
  if int(d.m_tvalid.value) and int(d.m_tready.value):
   output_cycles.append(cycle); outputs.append(int(d.m_tdata.value)); assert int(d.m_tuser.value)==(len(outputs)==1); assert int(d.m_tlast.value)==((len(outputs)-1)%W==W-1)
  await RisingEdge(d.clk); cycle+=1
  if cycle>2*N+5000: raise AssertionError('performance timeout')
 assert ins==N and len(outputs)==N
 count=await apb(d,12)
 def deltas(xs): return [b-a for a,b in zip(xs,xs[1:])]
 idi=deltas(input_cycles); odi=deltas(output_cycles)
 result={'dimensions':f'{W}x{H}','accepted_input_count':ins,'accepted_output_count':len(outputs),'frame_count':count,'first_input_cycle':input_cycles[0],'last_input_cycle':input_cycles[-1],'first_output_cycle':output_cycles[0],'last_output_cycle':output_cycles[-1],'first_output_latency_cycles':output_cycles[0]-input_cycles[0],'frame_completion_cycles':output_cycles[-1]-input_cycles[0]+1,'input_ii_min':min(idi),'input_ii_max':max(idi),'output_ii_min':min(odi),'output_ii_max':max(odi),'metadata_correct':True}
 out=os.environ['PERF_JSON']; json.dump(result,open(out,'w'),indent=2); print('PERF_RESULT',json.dumps(result,sort_keys=True))
 assert count==1 and result['input_ii_max']==1 and result['output_ii_max']==1
