import os
import cocotb
import numpy as np
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from tb.reference.sobel_reference import compare_gray, sobel_rgb

W=int(os.environ['IMG_WIDTH']); H=int(os.environ['IMG_HEIGHT']); N=W*H
CONTROL=0; THRESHOLD=4; STATUS=8; FRAME_COUNT=12
def rgb(f):
 a=np.empty((H,W,3),dtype=np.uint8)
 for r in range(H):
  for c in range(W): a[r,c]=((17*r+31*c+29*f+3)&255,(43*r+11*c+71*f+19)&255,(7*r+53*c+37*f+101)&255)
 return a
def pack(p): return (int(p[0])<<16)|(int(p[1])<<8)|int(p[2])
async def settle(): await Timer(1,unit='ns')
async def reset(d):
 cocotb.start_soon(Clock(d.clk,10,unit='ns').start()); d.rst.value=1; d.s_tvalid.value=0; d.m_tready.value=0; d.psel.value=0; d.penable.value=0; d.pwrite.value=0; d.paddr.value=0; d.pwdata.value=0
 await RisingEdge(d.clk); await RisingEdge(d.clk); d.rst.value=0; await settle(); assert not int(d.m_tvalid.value)
async def apb(d,addr,val=None):
 d.psel.value=1; d.penable.value=0; d.pwrite.value=int(val is not None); d.paddr.value=addr; d.pwdata.value=0 if val is None else val; await RisingEdge(d.clk); d.penable.value=1; await settle(); assert int(d.pready.value)==1 and int(d.pslverr.value)==0; out=int(d.prdata.value); await RisingEdge(d.clk); d.psel.value=0; d.penable.value=0; d.pwrite.value=0; d.paddr.value=0; d.pwdata.value=0; await settle(); return out
async def configure(d,t,b,run=1): await apb(d,CONTROL,run|(b<<1)); await apb(d,THRESHOLD,t)
def drive(d,a,i):
 r,c=divmod(i,W); d.s_tdata.value=pack(a[r,c]); d.s_tvalid.value=1; d.s_tuser.value=int(i==0); d.s_tlast.value=int(c==W-1)
def idle(d): d.s_tvalid.value=0; d.s_tdata.value=0; d.s_tuser.value=0; d.s_tlast.value=0
async def frame(d,a,t,b,stall_final=False):
 ins=0; outs=[]; maxc=20*N+200; d.m_tready.value=1
 for _ in range(maxc):
  if ins<N: drive(d,a,ins)
  else: idle(d)
  await settle(); inf=int(d.s_tvalid.value)&int(d.s_tready.value); outf=int(d.m_tvalid.value)&int(d.m_tready.value)
  if outf:
   oi=len(outs); r,c=divmod(oi,W); assert int(d.m_tuser.value)==(oi==0); assert int(d.m_tlast.value)==(c==W-1); outs.append(int(d.m_tdata.value))
  await RisingEdge(d.clk); ins+=inf; await settle()
  if stall_final and len(outs)==N-1 and int(d.m_tvalid.value):
   d.m_tready.value=0; await settle(); break
  if ins==N and len(outs)==N: break
 else: raise AssertionError('timeout')
 return ins,outs
def compare(a,vals,t,b,ins):
 assert ins==N and len(vals)==N
 exp=sobel_rgb(a,threshold=t,bypass_threshold=bool(b)); act=np.array(vals,dtype=np.uint8).reshape(H,W); res=compare_gray(exp,act); print(f"frame compare: threshold={t} bypass={b} accepted_input={ins} accepted_output={len(vals)} mismatch_count={res['mismatch_count']}"); assert res['mismatch_count']==0, res['mismatches']
 # The regression log records the actual frame counts and oracle result.
 return res['mismatch_count']
@cocotb.test()
async def run_enable_gates_and_bypass_frame_matches_reference(d):
 await reset(d); a=rgb(0); d.m_tready.value=1; drive(d,a,0); await settle(); assert int(d.s_tready.value)==0; idle(d); await configure(d,255,1); ins,vals=await frame(d,a,255,1); compare(a,vals,255,1,ins); assert await apb(d,FRAME_COUNT)==1; assert await apb(d,STATUS)&15==0
@cocotb.test()
async def thresholded_complete_frame_matches_reference(d):
 await reset(d); a=rgb(1); await configure(d,96,0); ins,vals=await frame(d,a,96,0); compare(a,vals,96,0,ins); assert await apb(d,FRAME_COUNT)==1; assert await apb(d,STATUS)&15==0
@cocotb.test()
async def final_output_stall_delays_count_and_new_frame_admission(d):
 await reset(d); a=rgb(2); await configure(d,128,1); ins,vals=await frame(d,a,128,1,True); assert ins==N and len(vals)==N-1; nexta=rgb(3); drive(d,nexta,0); await settle(); snap=(int(d.m_tdata.value),int(d.m_tuser.value),int(d.m_tlast.value)); assert int(d.m_tvalid.value) and not int(d.s_tready.value); assert await apb(d,FRAME_COUNT)==0; st=await apb(d,STATUS); assert (st&3)==3
 for _ in range(3): await RisingEdge(d.clk); await settle(); assert (int(d.m_tdata.value),int(d.m_tuser.value),int(d.m_tlast.value))==snap and not int(d.s_tready.value)
 d.m_tready.value=1; await settle(); vals.append(int(d.m_tdata.value)); await RisingEdge(d.clk); idle(d); await settle(); compare(a,vals,128,1,N); assert await apb(d,FRAME_COUNT)==1; assert await apb(d,STATUS)&15==0; drive(d,nexta,0); await settle(); assert int(d.s_tready.value)==1; idle(d)
@cocotb.test()
async def consecutive_frames_with_idle_reconfiguration_match_reference(d):
 await reset(d); a0=rgb(4); a1=rgb(5); await configure(d,48,0); ins,v=await frame(d,a0,48,0); compare(a0,v,48,0,ins); assert await apb(d,FRAME_COUNT)==1; await configure(d,200,0); ins,v=await frame(d,a1,200,0); compare(a1,v,200,0,ins); assert await apb(d,FRAME_COUNT)==2; assert await apb(d,STATUS)&15==0
