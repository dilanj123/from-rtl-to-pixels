module output_control_formal #(
    parameter int unsigned IMG_WIDTH  = 3,
    parameter int unsigned IMG_HEIGHT = 3
) (
    input logic clk
);

    localparam int unsigned ROW_W = $clog2(IMG_HEIGHT);
    localparam int unsigned COL_W = $clog2(IMG_WIDTH);
    localparam logic [ROW_W-1:0] LAST_ROW = ROW_W'(IMG_HEIGHT - 1);
    localparam logic [COL_W-1:0] LAST_COL = COL_W'(IMG_WIDTH - 1);

    (* anyseq *) logic rst;
    (* anyseq *) logic pixel_commit_i;
    (* anyseq *) logic frame_start_i;
    (* anyseq *) logic last_input_accept_i;
    (* anyseq *) logic frame_abort_i;
    (* anyseq *) logic output_ready_i;

    logic input_allow_o;
    logic output_valid_o;
    logic [ROW_W-1:0] output_row_o;
    logic [COL_W-1:0] output_col_o;
    logic output_border_o;
    logic processing_o;
    logic draining_o;
    logic waiting_for_sof_o;
    logic frame_done_o;

    logic f_past_valid = 1'b0;
    logic f_final_output_position;

    assign f_final_output_position =
        (output_row_o == LAST_ROW) && (output_col_o == LAST_COL);

    output_control #(
        .IMG_WIDTH  (IMG_WIDTH),
        .IMG_HEIGHT (IMG_HEIGHT)
    ) dut (
        .clk                 (clk),
        .rst                 (rst),
        .pixel_commit_i      (pixel_commit_i),
        .frame_start_i       (frame_start_i),
        .last_input_accept_i (last_input_accept_i),
        .frame_abort_i       (frame_abort_i),
        .output_ready_i      (output_ready_i),
        .input_allow_o       (input_allow_o),
        .output_valid_o      (output_valid_o),
        .output_row_o        (output_row_o),
        .output_col_o        (output_col_o),
        .output_border_o     (output_border_o),
        .processing_o        (processing_o),
        .draining_o          (draining_o),
        .waiting_for_sof_o   (waiting_for_sof_o),
        .frame_done_o        (frame_done_o)
    );

    always_ff @(posedge clk) begin
        if (!f_past_valid) begin
            assume(rst);
        end

        f_past_valid <= 1'b1;

        if (f_past_valid) begin
            a_f_out_state_mutual_exclusion_process_drain:
                assert(!(processing_o && draining_o));
            a_f_out_state_mutual_exclusion_process_wait:
                assert(!(processing_o && waiting_for_sof_o));
            a_f_out_state_mutual_exclusion_drain_wait:
                assert(!(draining_o && waiting_for_sof_o));
        end

        if (f_past_valid && draining_o) begin
            a_f_out_001_no_input_during_drain:
                assert(!input_allow_o);
            a_f_out_001_not_processing_during_drain:
                assert(!processing_o);
            a_f_out_001_not_waiting_during_drain:
                assert(!waiting_for_sof_o);
        end

        if (f_past_valid && draining_o && !rst && !frame_abort_i) begin
            a_f_out_drain_valid:
                assert(output_valid_o);
        end

        if (f_past_valid) begin
            a_f_out_frame_done_definition:
                assert(
                    frame_done_o ==
                    (!rst && !frame_abort_i && draining_o &&
                     output_valid_o && output_ready_i &&
                     f_final_output_position)
                );
        end

        if (
            f_past_valid && !rst && !frame_abort_i && !$past(rst) &&
            !$past(frame_abort_i) && $past(draining_o && !output_ready_i)
        ) begin
            a_f_out_002_stall_keeps_drain: assert(draining_o);
            a_f_out_002_stall_keeps_valid: assert(output_valid_o);
            a_f_out_002_stall_row_stable:
                assert(output_row_o == $past(output_row_o));
            a_f_out_002_stall_col_stable:
                assert(output_col_o == $past(output_col_o));
        end

        if (
            f_past_valid && !rst && !frame_abort_i && !$past(rst) &&
            !$past(frame_abort_i) &&
            $past(draining_o && output_ready_i &&
                  !(output_row_o == LAST_ROW && output_col_o == LAST_COL))
        ) begin
            a_f_out_002_ready_nonfinal_stays_drain:
                assert(draining_o);
            if ($past(output_col_o == LAST_COL)) begin
                a_f_out_002_eol_col_zero:
                    assert(output_col_o == COL_W'(0));
                a_f_out_002_eol_row_increment:
                    assert(output_row_o == $past(output_row_o) + ROW_W'(1));
            end else begin
                a_f_out_002_inner_row_stable:
                    assert(output_row_o == $past(output_row_o));
                a_f_out_002_inner_col_increment:
                    assert(output_col_o == $past(output_col_o) + COL_W'(1));
            end
        end

        if (f_past_valid && $past(frame_done_o)) begin
            a_f_out_002_final_returns_wait: assert(waiting_for_sof_o);
            a_f_out_002_final_leaves_drain: assert(!draining_o);
            a_f_out_002_final_leaves_process: assert(!processing_o);
        end

        if (f_past_valid && ($past(rst) || $past(frame_abort_i))) begin
            a_f_out_reset_abort_wait: assert(waiting_for_sof_o);
            a_f_out_reset_abort_not_processing: assert(!processing_o);
            a_f_out_reset_abort_not_draining: assert(!draining_o);
        end

        c_enter_process:
            cover(f_past_valid && !rst && processing_o);
        c_enter_drain:
            cover(f_past_valid && !rst && !frame_abort_i && draining_o);
        c_drain_input_blocked:
            cover(f_past_valid && !rst && !frame_abort_i && draining_o &&
                  !input_allow_o);
        c_drain_stall:
            cover(f_past_valid && !rst && !frame_abort_i && draining_o &&
                  output_valid_o && !output_ready_i);
        c_drain_stall_then_ready:
            cover(f_past_valid && !rst && !frame_abort_i && !$past(rst) &&
                  !$past(frame_abort_i) &&
                  $past(draining_o && !output_ready_i) &&
                  draining_o && output_ready_i);
        c_drain_ready_nonfinal:
            cover(f_past_valid && !rst && !frame_abort_i && draining_o &&
                  output_ready_i && !f_final_output_position);
        c_frame_done:
            cover(f_past_valid && frame_done_o);
        c_frame_done_returned_wait:
            cover(f_past_valid && $past(frame_done_o) && waiting_for_sof_o);
        c_abort_during_drain:
            cover(f_past_valid && draining_o && frame_abort_i);
        c_reset_during_drain:
            cover(f_past_valid && draining_o && rst);
    end

endmodule
