import os, random
import cocotb
import numpy as np
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from tb.reference.sobel_reference import compare_gray, sobel_rgb

W=int(os.environ['IMG_WIDTH']); H=int(os.environ['IMG_HEIGHT']); N=W*H; D=W+1
CONTROL=0; THRESHOLD=4; STATUS=8; FRAME_COUNT=12
async def settle(): await Timer(1,unit='ns')
def coord(i): return divmod(i,W)
def image(seed): return np.random.default_rng(seed).integers(0,256,size=(H,W,3),dtype=np.uint8)
def pack(p): return (int(p[0])<<16)|(int(p[1])<<8)|int(p[2])
async def reset(d):
 cocotb.start_soon(Clock(d.clk,10,unit='ns').start()); d.rst.value=1; d.s_tvalid.value=0; d.m_tready.value=0; d.psel.value=0; d.penable.value=0; d.pwrite.value=0; d.paddr.value=0; d.pwdata.value=0
 await RisingEdge(d.clk); await RisingEdge(d.clk); d.rst.value=0; await settle()
async def apb(d,a,v=None):
 d.psel.value=1; d.penable.value=0; d.pwrite.value=int(v is not None); d.paddr.value=a; d.pwdata.value=0 if v is None else v; await RisingEdge(d.clk); d.penable.value=1; await settle(); assert int(d.pready.value)==1 and int(d.pslverr.value)==0; x=int(d.prdata.value); await RisingEdge(d.clk); d.psel.value=0; d.penable.value=0; d.pwrite.value=0; d.paddr.value=0; d.pwdata.value=0; await settle(); return x
async def config(d,t,b): await apb(d,CONTROL,1|(b<<1)); await apb(d,THRESHOLD,t)
def idle(d): d.s_tvalid.value=0; d.s_tdata.value=0; d.s_tuser.value=0; d.s_tlast.value=0
def drive(d,a,i):
 r,c=coord(i); d.s_tdata.value=pack(a[r,c]); d.s_tvalid.value=1; d.s_tuser.value=int(i==0); d.s_tlast.value=int(c==W-1)
def check_pending(pending, valid, transaction):
 if pending is not None:
  assert valid, 'm_tvalid dropped before stalled transaction transferred'
  assert transaction == pending, 'stalled output data/metadata changed'

class Ready:
 def __init__(self,mode,seed):
  self.mode=mode; self.r=random.Random(seed); self.used={}
 def targets(self):
  if self.mode=='metadata': return {i:2 for i in [0]+list(range(W-1,N,W))}
  if self.mode=='drain': return {i:(4 if i==N-1 else 3 if i==N-D else 1) for i in range(N-D,N)}
  return {}
 def get(self,cycle,oi,valid):
  if self.mode=='always': return 1
  if self.mode=='random': return 0 if cycle%23 in (7,8,9) else int(self.r.random()>=.35)
  if self.mode in ('metadata','drain'):
   return int(not (valid and self.used.get(oi,0)<self.targets().get(oi,0)))
  raise ValueError(self.mode)
 def observe_stall(self,oi):
  self.used[oi]=self.used.get(oi,0)+1
 def verify_coverage(self):
  targets=self.targets()
  for i,count in targets.items():
   assert self.used.get(i,0)==count, f'{self.mode} output {i}: expected {count} stalls, observed {self.used.get(i,0)}'
  if targets: print(f'targeted_stall_coverage: mode={self.mode} expected={targets} observed={self.used}')
async def run(d,a,t,b,source_seed,gapmax,mode,ready_seed):
 await config(d,t,b); rng=random.Random(source_seed); gaps=[rng.randrange(gapmax+1) for _ in range(N)]; ready=Ready(mode,ready_seed); ii=0; out=[]; gap=0; holding=False; snap=None; gapc=stallc=0
 for cyc in range(100*N+2000):
  valid=int(d.m_tvalid.value); oi=len(out); d.m_tready.value=ready.get(cyc,oi,valid)
  if ii>=N: idle(d)
  elif holding: drive(d,a,ii)
  elif gap: idle(d); gapc+=1
  else: holding=True; drive(d,a,ii)
  await settle(); inf=bool(int(d.s_tvalid.value) and int(d.s_tready.value)); ov=bool(d.m_tvalid.value); ot=ov and bool(d.m_tready.value)
  cur=(int(d.m_tdata.value),int(d.m_tuser.value),int(d.m_tlast.value))
  check_pending(snap,ov,cur)
  if ov and not ot:
   ready.observe_stall(oi)
   stallc+=1; cur=(int(d.m_tdata.value),int(d.m_tuser.value),int(d.m_tlast.value)); snap=cur if snap is None else snap; assert cur==snap
  if ot:
   assert snap is None or (int(d.m_tdata.value),int(d.m_tuser.value),int(d.m_tlast.value))==snap; snap=None; r,c=coord(len(out)); assert int(d.m_tuser.value)==(len(out)==0); assert int(d.m_tlast.value)==(c==W-1); out.append(int(d.m_tdata.value))
  await RisingEdge(d.clk)
  if inf: ii+=1; holding=False; gap=gaps[ii] if ii<N else 0
  elif not holding and gap: gap-=1
  await settle()
  if ii==N and len(out)==N: break
 else: raise AssertionError('stress timeout')
 ready.verify_coverage()
 idle(d); d.m_tready.value=1; await settle(); assert not int(d.m_tvalid.value); act=np.array(out,dtype=np.uint8).reshape(H,W); res=compare_gray(sobel_rgb(a,threshold=t,bypass_threshold=bool(b)),act); print(f'stream stress frame: ready_mode={mode} accepted_input={ii} accepted_output={len(out)} source_gap_cycles={gapc} output_stall_cycles={stallc} mismatch_count={res["mismatch_count"]}'); assert ii==N and len(out)==N and res['mismatch_count']==0; assert await apb(d,FRAME_COUNT)==1; assert await apb(d,STATUS)&15==0; return gapc,stallc
@cocotb.test()
async def randomized_source_gaps_match_reference(d): await reset(d); g,s=await run(d,image(0x1001),73,0,0x2001,4,'always',0); assert g>0
@cocotb.test()
async def randomized_downstream_backpressure_is_bit_exact(d): await reset(d); g,s=await run(d,image(0x1002),191,1,0,0,'random',0x3002); assert s>0
@cocotb.test()
async def combined_random_gaps_and_backpressure_match_reference(d): await reset(d); g,s=await run(d,image(0x1003),128,0,0x2003,3,'random',0x3003); assert g>0 and s>0
@cocotb.test()
async def sof_and_eol_output_stalls_are_stable(d): await reset(d); g,s=await run(d,image(0x1004),37,1,0x2004,2,'metadata',0); assert s>0
@cocotb.test()
async def drain_backpressure_preserves_exact_frame(d): await reset(d); g,s=await run(d,image(0x1005),211,0,0x2005,2,'drain',0); assert s>0
