module rtl_to_pixels_top_pipelined #(
    parameter int unsigned IMG_WIDTH=640, IMG_HEIGHT=480
) (
    input logic clk,input logic rst,input logic [23:0] s_tdata,input logic s_tvalid,output logic s_tready,
    input logic s_tuser,input logic s_tlast,output logic [7:0] m_tdata,output logic m_tvalid,input logic m_tready,
    output logic m_tuser,output logic m_tlast,input logic psel,input logic penable,input logic pwrite,
    input logic [7:0] paddr,input logic [31:0] pwdata,output logic [31:0] prdata,output logic pready,output logic pslverr
);
    localparam int ROW_W=$clog2(IMG_HEIGHT); localparam int COL_W=$clog2(IMG_WIDTH);
    localparam logic [COL_W-1:0] LAST_COL=COL_W'(IMG_WIDTH-1);
    logic run_enable; logic [7:0] threshold_active; logic bypass_threshold_active;
    logic input_accept; logic [ROW_W-1:0] input_row; logic [COL_W-1:0] input_col;
    logic pixel_commit,sof_accept,last_input_accept,metadata_error,pixel_waiting_for_sof,frame_abort_q;
    logic [7:0] gray_pixel,prev_row1,prev_row2; logic prev_row1_valid,prev_row2_valid;
    logic window_valid; logic [ROW_W-1:0] window_row; logic [COL_W-1:0] window_col;
    logic [7:0] p00,p01,p02,p10,p11,p12,p20,p21,p22; logic signed [11:0] gx,gy;
    logic [27:0] arithmetic_s_data,arithmetic_m_data;
    logic arithmetic_s_ready,arithmetic_m_valid;
    logic staged_final_tag,staged_user,staged_last,staged_border;
    logic signed [11:0] staged_gx,staged_gy;
    logic [10:0] magnitude; logic [7:0] magnitude_clamped,threshold_edge,staged_output_data;
    logic output_input_allow,raw_output_valid; logic [ROW_W-1:0] raw_output_row; logic [COL_W-1:0] raw_output_col;
    logic raw_output_border,processing_internal,draining_internal,output_waiting_for_sof,raw_frame_done_internal;
    logic raw_output_user,raw_output_last,output_elastic_s_ready,pipeline_rst;
    logic [10:0] output_elastic_s_data,output_elastic_m_data; logic output_elastic_m_valid,final_pending_q,frame_done_external,draining_status;
    wire _unused_ok=1'b0 && &{1'b0,window_valid,window_row,window_col,p10,p11,magnitude,1'b0};
    always_comb begin
      s_tready=1'b0;
      if(!rst&&!frame_abort_q&&!final_pending_q&&output_input_allow)
        s_tready=pixel_waiting_for_sof?(output_waiting_for_sof&&run_enable&&s_tuser):1'b1;
    end
    assign input_accept=s_tvalid&&s_tready;
    pixel_control #(.IMG_WIDTH(IMG_WIDTH),.IMG_HEIGHT(IMG_HEIGHT)) u_pixel_control(
      .clk(clk),.rst(rst),.accept_i(input_accept),.s_tuser_i(s_tuser),.s_tlast_i(s_tlast),.row_o(input_row),.col_o(input_col),
      .pixel_commit_o(pixel_commit),.sof_accept_o(sof_accept),.last_input_accept_o(last_input_accept),.metadata_error_o(metadata_error),.waiting_for_sof_o(pixel_waiting_for_sof));
    always_ff @(posedge clk) if(rst) frame_abort_q<=0; else frame_abort_q<=metadata_error;
    rgb_to_gray u_rgb_to_gray(.rgb_i(s_tdata),.gray_o(gray_pixel));
    line_buffer #(.DATA_WIDTH(8),.IMG_WIDTH(IMG_WIDTH)) u_line_buffer(.clk(clk),.rst(rst),.pixel_commit_i(pixel_commit),.frame_start_i(sof_accept),.col_i(input_col),.pixel_i(gray_pixel),.prev_row1_o(prev_row1),.prev_row1_valid_o(prev_row1_valid),.prev_row2_o(prev_row2),.prev_row2_valid_o(prev_row2_valid));
    window_3x3 #(.DATA_WIDTH(8),.IMG_WIDTH(IMG_WIDTH),.IMG_HEIGHT(IMG_HEIGHT)) u_window(.clk(clk),.rst(rst),.pixel_commit_i(pixel_commit),.frame_start_i(sof_accept),.row_i(input_row),.col_i(input_col),.pixel_i(gray_pixel),.prev_row1_i(prev_row1),.prev_row1_valid_i(prev_row1_valid),.prev_row2_i(prev_row2),.prev_row2_valid_i(prev_row2_valid),.window_valid_o(window_valid),.window_row_o(window_row),.window_col_o(window_col),.p00_o(p00),.p01_o(p01),.p02_o(p02),.p10_o(p10),.p11_o(p11),.p12_o(p12),.p20_o(p20),.p21_o(p21),.p22_o(p22));
    sobel_compact u_sobel(.p00_i(p00),.p01_i(p01),.p02_i(p02),.p10_i(p10),.p12_i(p12),.p20_i(p20),.p21_i(p21),.p22_i(p22),.gx_o(gx),.gy_o(gy));
    output_control #(.IMG_WIDTH(IMG_WIDTH),.IMG_HEIGHT(IMG_HEIGHT)) u_output_control(.clk(clk),.rst(rst),.pixel_commit_i(pixel_commit),.frame_start_i(sof_accept),.last_input_accept_i(last_input_accept),.frame_abort_i(frame_abort_q),.output_ready_i(arithmetic_s_ready),.input_allow_o(output_input_allow),.output_valid_o(raw_output_valid),.output_row_o(raw_output_row),.output_col_o(raw_output_col),.output_border_o(raw_output_border),.processing_o(processing_internal),.draining_o(draining_internal),.waiting_for_sof_o(output_waiting_for_sof),.frame_done_o(raw_frame_done_internal));
    assign raw_output_user=(raw_output_row==ROW_W'(0))&&(raw_output_col==COL_W'(0));
    assign raw_output_last=(raw_output_col==LAST_COL);
    assign arithmetic_s_data={raw_frame_done_internal,raw_output_user,raw_output_last,raw_output_border,gx,gy};
    assign pipeline_rst=rst||metadata_error||frame_abort_q;
    elastic_stage #(.DATA_WIDTH(28)) u_arithmetic_elastic(.clk(clk),.rst(pipeline_rst),.s_data(arithmetic_s_data),.s_valid(raw_output_valid),.s_ready(arithmetic_s_ready),.m_data(arithmetic_m_data),.m_valid(arithmetic_m_valid),.m_ready(output_elastic_s_ready));
    assign staged_final_tag=arithmetic_m_data[27]; assign staged_user=arithmetic_m_data[26]; assign staged_last=arithmetic_m_data[25]; assign staged_border=arithmetic_m_data[24];
    assign staged_gx=$signed(arithmetic_m_data[23:12]); assign staged_gy=$signed(arithmetic_m_data[11:0]);
    magnitude_clamp u_magnitude(.gx_i(staged_gx),.gy_i(staged_gy),.magnitude_o(magnitude),.magnitude_clamped_o(magnitude_clamped));
    threshold_stage u_threshold(.magnitude_i(magnitude_clamped),.threshold_i(threshold_active),.bypass_threshold_i(bypass_threshold_active),.edge_o(threshold_edge));
    always_comb staged_output_data=staged_border?8'd0:threshold_edge;
    assign output_elastic_s_data={staged_final_tag,staged_user,staged_last,staged_output_data};
    elastic_stage #(.DATA_WIDTH(11)) u_output_elastic(.clk(clk),.rst(pipeline_rst),.s_data(output_elastic_s_data),.s_valid(arithmetic_m_valid),.s_ready(output_elastic_s_ready),.m_data(output_elastic_m_data),.m_valid(output_elastic_m_valid),.m_ready(m_tready));
    assign m_tdata=output_elastic_m_data[7:0]; assign m_tlast=output_elastic_m_data[8]; assign m_tuser=output_elastic_m_data[9]; assign m_tvalid=output_elastic_m_valid;
    assign frame_done_external=output_elastic_m_valid&&m_tready&&output_elastic_m_data[10];
    always_ff @(posedge clk) begin
      if(rst||metadata_error) final_pending_q<=1'b0;
      else if(frame_done_external) final_pending_q<=1'b0;
      else if(raw_frame_done_internal) final_pending_q<=1'b1;
    end
    assign draining_status=draining_internal||final_pending_q;
    apb_regs u_apb_regs(.clk(clk),.rst(rst),.psel(psel),.penable(penable),.pwrite(pwrite),.paddr(paddr),.pwdata(pwdata),.prdata(prdata),.pready(pready),.pslverr(pslverr),.processing_i(processing_internal),.draining_i(draining_status),.sof_accept_i(sof_accept),.frame_error_set_i(metadata_error),.frame_done_i(frame_done_external),.run_enable_o(run_enable),.threshold_active_o(threshold_active),.bypass_threshold_active_o(bypass_threshold_active));
endmodule
