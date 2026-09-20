import os
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

W=int(os.environ['IMG_WIDTH']); H=int(os.environ['IMG_HEIGHT']); N=W*H; FILL=W+1
def label(f,r,c): return (101*f+16*r+c+1)&255
def coord(i): return divmod(i,W)
def border(r,c): return r==0 or r==H-1 or c==0 or c==W-1
def taps(f,r,c): return tuple(label(f,rr,cc) for rr,cc in ((r-1,c-1),(r-1,c),(r-1,c+1),(r,c-1),(r,c),(r,c+1),(r+1,c-1),(r+1,c),(r+1,c+1)))
def calc(v):
 p00,p01,p02,p10,_,p12,p20,p21,p22=v
 gx=-p00+p02-2*p10+2*p12-p20+p22; gy=-p00-2*p01-p02+p20+2*p21+p22
 m=abs(gx)+abs(gy); return gx,gy,m,min(m,255)
def s12(x):
 x=int(x.value); return x-(1<<12) if x&(1<<11) else x
async def settle(): await Timer(1,unit='ns')
async def reset(d):
 cocotb.start_soon(Clock(d.clk,10,unit='ns').start()); d.rst.value=1; d.in_valid_i.value=0; d.out_ready_i.value=0; d.frame_abort_i.value=0; d.threshold_i.value=128; d.bypass_threshold_i.value=0
 await RisingEdge(d.clk); await RisingEdge(d.clk); d.rst.value=0; await settle(); assert int(d.waiting_for_sof_o.value)==1
def set_inputs(d,f,i,threshold,bypass):
 r,c=coord(i); d.in_valid_i.value=1; d.in_pixel_i.value=label(f,r,c); d.in_row_i.value=r; d.in_col_i.value=c; d.frame_start_i.value=int(i==0); d.last_input_i.value=int(i==N-1); d.threshold_i.value=threshold; d.bypass_threshold_i.value=bypass
async def inspect(d,f,oi,threshold,bypass,ready):
 r,c=coord(oi); b=border(r,c); assert int(d.out_valid_o.value)==1 and int(d.out_row_o.value)==r and int(d.out_col_o.value)==c; assert int(d.out_border_o.value)==b and int(d.alignment_error_o.value)==0
 if b: assert int(d.out_data_o.value)==0 and int(d.window_valid_o.value)==0
 else:
  t=taps(f,r,c); assert int(d.window_valid_o.value)==1 and (int(d.window_row_o.value),int(d.window_col_o.value))==(r,c); assert tuple(int(getattr(d,n+'_o').value) for n in ('p00','p01','p02','p10','p11','p12','p20','p21','p22'))==t
  gx,gy,m,mc=calc(t); assert (s12(d.gx_o),s12(d.gy_o),int(d.magnitude_o.value),int(d.magnitude_clamped_o.value))==(gx,gy,m,mc); assert int(d.threshold_edge_o.value)==(mc if bypass or mc>=threshold else 0) and int(d.out_data_o.value)==(mc if bypass or mc>=threshold else 0)
 assert int(d.frame_done_o.value)==int(ready and oi==N-1 and d.draining_o.value)
async def run_frame(d,f,threshold,bypass,gaps=False,stalls=False,drain_stalls=False):
 live=0
 for i in range(N):
  if gaps and i%3:
   d.in_valid_i.value=0; d.out_ready_i.value=1; await settle(); assert not int(d.pixel_commit_o.value); await RisingEdge(d.clk); await settle()
  set_inputs(d,f,i,threshold,bypass)
  if stalls and i>=FILL and i%4==0:
   for _ in range(2): d.out_ready_i.value=0; await settle(); assert int(d.in_ready_o.value)==0 and not int(d.pixel_commit_o.value); await RisingEdge(d.clk); await settle()
  d.out_ready_i.value=1; await settle(); assert int(d.in_ready_o.value)==1 and int(d.pixel_commit_o.value)==1
  if i>=FILL: await inspect(d,f,i-FILL,threshold,bypass,1); live+=1
  else: assert not int(d.out_valid_o.value) and not int(d.window_valid_o.value)
  await RisingEdge(d.clk); await settle()
 for oi in range(live,N):
  for _ in range((oi%2 if drain_stalls else 0)):
   d.out_ready_i.value=0; await settle(); snap=(int(d.out_row_o.value),int(d.out_col_o.value),int(d.out_border_o.value),int(d.out_data_o.value)); await inspect(d,f,oi,threshold,bypass,0); await RisingEdge(d.clk); await settle(); assert snap==(int(d.out_row_o.value),int(d.out_col_o.value),int(d.out_border_o.value),int(d.out_data_o.value))
  d.out_ready_i.value=1; await settle(); await inspect(d,f,oi,threshold,bypass,1); await RisingEdge(d.clk); await settle()
 assert live==N-FILL and N-live==W+1 and int(d.waiting_for_sof_o.value)==1
@cocotb.test()
async def labelled_frame_alignment(d): await reset(d); await run_frame(d,0,128,1)
@cocotb.test()
async def source_gaps_preserve_alignment(d): await reset(d); await run_frame(d,0,128,0,gaps=True)
@cocotb.test()
async def live_backpressure_blocks_commit(d): await reset(d); await run_frame(d,0,128,1,stalls=True)
@cocotb.test()
async def drain_backpressure_is_stable(d): await reset(d); await run_frame(d,0,128,1,drain_stalls=True)
@cocotb.test()
async def consecutive_frames_are_isolated(d): await reset(d); await run_frame(d,0,0,1); await run_frame(d,1,200,0,gaps=True,stalls=True,drain_stalls=True)
