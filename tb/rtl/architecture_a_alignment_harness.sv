module architecture_a_alignment_harness #(
    parameter int unsigned IMG_WIDTH=5,
    parameter int unsigned IMG_HEIGHT=4
) (
    input logic clk,input logic rst,input logic in_valid_i,input logic [7:0] in_pixel_i,
    input logic [$clog2(IMG_HEIGHT)-1:0] in_row_i,input logic [$clog2(IMG_WIDTH)-1:0] in_col_i,
    input logic frame_start_i,input logic last_input_i,input logic frame_abort_i,
    output logic in_ready_o,output logic pixel_commit_o,input logic out_ready_i,
    input logic [7:0] threshold_i,input logic bypass_threshold_i,output logic out_valid_o,
    output logic [$clog2(IMG_HEIGHT)-1:0] out_row_o,output logic [$clog2(IMG_WIDTH)-1:0] out_col_o,
    output logic out_border_o,output logic [7:0] out_data_o,output logic processing_o,
    output logic draining_o,output logic waiting_for_sof_o,output logic frame_done_o,
    output logic window_valid_o,output logic [$clog2(IMG_HEIGHT)-1:0] window_row_o,
    output logic [$clog2(IMG_WIDTH)-1:0] window_col_o,output logic [7:0] p00_o,p01_o,p02_o,
    output logic [7:0] p10_o,p11_o,p12_o,p20_o,p21_o,p22_o,
    output logic signed [11:0] gx_o,output logic signed [11:0] gy_o,
    output logic [10:0] magnitude_o,output logic [7:0] magnitude_clamped_o,
    output logic [7:0] threshold_edge_o,output logic alignment_error_o
);
    logic frame_start_commit,last_input_commit;
    logic [7:0] prev_row1,prev_row2; logic prev_row1_valid,prev_row2_valid;
    assign pixel_commit_o=in_valid_i&&in_ready_o;
    assign frame_start_commit=pixel_commit_o&&frame_start_i;
    assign last_input_commit=pixel_commit_o&&last_input_i;
    line_buffer #(.DATA_WIDTH(8),.IMG_WIDTH(IMG_WIDTH)) u_line_buffer(
      .clk(clk),.rst(rst),.pixel_commit_i(pixel_commit_o),.frame_start_i(frame_start_commit),
      .col_i(in_col_i),.pixel_i(in_pixel_i),.prev_row1_o(prev_row1),.prev_row1_valid_o(prev_row1_valid),
      .prev_row2_o(prev_row2),.prev_row2_valid_o(prev_row2_valid));
    window_3x3 #(.DATA_WIDTH(8),.IMG_WIDTH(IMG_WIDTH),.IMG_HEIGHT(IMG_HEIGHT)) u_window(
      .clk(clk),.rst(rst),.pixel_commit_i(pixel_commit_o),.frame_start_i(frame_start_commit),
      .row_i(in_row_i),.col_i(in_col_i),.pixel_i(in_pixel_i),.prev_row1_i(prev_row1),
      .prev_row1_valid_i(prev_row1_valid),.prev_row2_i(prev_row2),.prev_row2_valid_i(prev_row2_valid),
      .window_valid_o(window_valid_o),.window_row_o(window_row_o),.window_col_o(window_col_o),
      .p00_o(p00_o),.p01_o(p01_o),.p02_o(p02_o),.p10_o(p10_o),.p11_o(p11_o),.p12_o(p12_o),
      .p20_o(p20_o),.p21_o(p21_o),.p22_o(p22_o));
    sobel_compact u_sobel(.p00_i(p00_o),.p01_i(p01_o),.p02_i(p02_o),.p10_i(p10_o),.p12_i(p12_o),
      .p20_i(p20_o),.p21_i(p21_o),.p22_i(p22_o),.gx_o(gx_o),.gy_o(gy_o));
    magnitude_clamp u_magnitude(.gx_i(gx_o),.gy_i(gy_o),.magnitude_o(magnitude_o),.magnitude_clamped_o(magnitude_clamped_o));
    threshold_stage u_threshold(.magnitude_i(magnitude_clamped_o),.threshold_i(threshold_i),
      .bypass_threshold_i(bypass_threshold_i),.edge_o(threshold_edge_o));
    output_control #(.IMG_WIDTH(IMG_WIDTH),.IMG_HEIGHT(IMG_HEIGHT)) u_output_control(
      .clk(clk),.rst(rst),.pixel_commit_i(pixel_commit_o),.frame_start_i(frame_start_commit),
      .last_input_accept_i(last_input_commit),.frame_abort_i(frame_abort_i),.output_ready_i(out_ready_i),
      .input_allow_o(in_ready_o),.output_valid_o(out_valid_o),.output_row_o(out_row_o),.output_col_o(out_col_o),
      .output_border_o(out_border_o),.processing_o(processing_o),.draining_o(draining_o),
      .waiting_for_sof_o(waiting_for_sof_o),.frame_done_o(frame_done_o));
    always_comb out_data_o=out_border_o?8'd0:threshold_edge_o;
    always_comb begin
      alignment_error_o=1'b0;
      if(!rst && window_valid_o && (!out_valid_o||out_border_o||window_row_o!=out_row_o||window_col_o!=out_col_o)) alignment_error_o=1'b1;
      if(!rst && out_valid_o && !out_border_o && (!window_valid_o||window_row_o!=out_row_o||window_col_o!=out_col_o)) alignment_error_o=1'b1;
    end
endmodule
