module frame_completion_formal #(
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
    (* anyseq *) logic event_valid_i;
    (* anyseq *) logic event_error_i;
    (* anyseq *) logic frame_start_i;
    (* anyseq *) logic last_input_accept_i;
    (* anyseq *) logic m_tready;

    logic f_past_valid = 1'b0;
    logic accepted_event, pixel_commit_i, metadata_error_i;
    logic frame_abort_q, output_input_allow;
    logic raw_output_valid;
    logic [ROW_W-1:0] raw_output_row;
    logic [COL_W-1:0] raw_output_col;
    logic raw_output_border;
    logic processing_internal, draining_internal, output_waiting_for_sof;
    logic raw_frame_done_internal;
    logic elastic_s_ready, elastic_rst;
    logic [10:0] elastic_s_data, elastic_m_data;
    logic elastic_m_valid;
    logic final_pending_q, frame_done_external, draining_status;
    logic sof_accept_i;
    logic [31:0] dut_frame_count_q;
    logic run_enable_unused;
    logic [7:0] threshold_active_unused;
    logic bypass_active_unused;
    logic [31:0] prdata_unused;
    logic pready_unused, pslverr_unused;

    assign accepted_event = event_valid_i && !rst && !frame_abort_q &&
        !final_pending_q && output_input_allow;
    assign pixel_commit_i = accepted_event && !event_error_i;
    assign metadata_error_i = accepted_event && event_error_i;
    assign sof_accept_i = pixel_commit_i && frame_start_i;

    always_ff @(posedge clk) begin
        if (rst) frame_abort_q <= 1'b0;
        else frame_abort_q <= metadata_error_i;
    end

    output_control #(.IMG_WIDTH(IMG_WIDTH), .IMG_HEIGHT(IMG_HEIGHT)) u_output_control (
        .clk(clk), .rst(rst), .pixel_commit_i(pixel_commit_i),
        .frame_start_i(frame_start_i), .last_input_accept_i(last_input_accept_i),
        .frame_abort_i(frame_abort_q), .output_ready_i(elastic_s_ready),
        .input_allow_o(output_input_allow), .output_valid_o(raw_output_valid),
        .output_row_o(raw_output_row), .output_col_o(raw_output_col),
        .output_border_o(raw_output_border), .processing_o(processing_internal),
        .draining_o(draining_internal), .waiting_for_sof_o(output_waiting_for_sof),
        .frame_done_o(raw_frame_done_internal)
    );

    assign elastic_s_data = {raw_frame_done_internal, 10'd0};
    assign elastic_rst = rst || metadata_error_i || frame_abort_q;

    elastic_stage #(.DATA_WIDTH(11)) u_output_elastic (
        .clk(clk), .rst(elastic_rst), .s_data(elastic_s_data),
        .s_valid(raw_output_valid), .s_ready(elastic_s_ready),
        .m_data(elastic_m_data), .m_valid(elastic_m_valid), .m_ready(m_tready)
    );

    assign frame_done_external = elastic_m_valid && m_tready && elastic_m_data[10];

    always_ff @(posedge clk) begin
        if (rst || metadata_error_i) final_pending_q <= 1'b0;
        else if (frame_done_external) final_pending_q <= 1'b0;
        else if (raw_frame_done_internal) final_pending_q <= 1'b1;
    end

    assign draining_status = draining_internal || final_pending_q;

    apb_regs u_apb_regs (
        .clk(clk), .rst(rst), .psel(1'b0), .penable(1'b0), .pwrite(1'b0),
        .paddr(8'd0), .pwdata(32'd0), .prdata(prdata_unused),
        .pready(pready_unused), .pslverr(pslverr_unused),
        .processing_i(processing_internal), .draining_i(draining_status),
        .sof_accept_i(sof_accept_i), .frame_error_set_i(metadata_error_i),
        .frame_done_i(frame_done_external), .run_enable_o(run_enable_unused),
        .threshold_active_o(threshold_active_unused),
        .bypass_threshold_active_o(bypass_active_unused),
        .frame_count_q(dut_frame_count_q)
    );

    always_ff @(posedge clk) begin
        if (!f_past_valid) assume(rst);
        f_past_valid <= 1'b1;

        if (f_past_valid) begin
            a_f_frame_commit_error_exclusive: assert(!(pixel_commit_i && metadata_error_i));
            a_f_frame_draining_status_definition:
                assert(draining_status == (draining_internal || final_pending_q));
            a_f_frame_external_done_definition:
                assert(frame_done_external == (elastic_m_valid && m_tready && elastic_m_data[10]));
        end

        if (f_past_valid && raw_frame_done_internal) begin
            a_f_frame_raw_done_has_valid: assert(raw_output_valid);
            a_f_frame_raw_done_has_elastic_admission: assert(elastic_s_ready);
            a_f_frame_raw_done_is_final_position:
                assert(raw_output_row == LAST_ROW && raw_output_col == LAST_COL);
        end

        if (f_past_valid)
            a_f_frame_internal_external_not_same_event:
                assert(!(raw_frame_done_internal && frame_done_external));

        if (f_past_valid && final_pending_q) begin
            a_f_frame_pending_keeps_draining_status: assert(draining_status);
            a_f_frame_pending_blocks_accept: assert(!accepted_event);
            a_f_frame_pending_blocks_commit: assert(!pixel_commit_i);
            a_f_frame_pending_blocks_metadata_error: assert(!metadata_error_i);
        end

        if (f_past_valid && $past(raw_frame_done_internal)) begin
            a_f_frame_raw_done_sets_pending: assert(final_pending_q);
            a_f_frame_raw_done_reaches_elastic:
                assert(elastic_m_valid && elastic_m_data[10]);
        end

        /*
         * --------------------------------------------------------------
         * Inductive final-token bridge invariants.
         *
         * These are assertions about reachable production integration
         * state. They are NOT environmental assumptions.
         * --------------------------------------------------------------
         */
        if (f_past_valid) begin
            a_f_frame_bridge_pending_matches_final_tag:
                assert(
                    final_pending_q ==
                    (elastic_m_valid && elastic_m_data[10])
                );

            if (final_pending_q) begin
                a_f_frame_bridge_pending_waits_for_external_transfer:
                    assert(output_waiting_for_sof);
                a_f_frame_bridge_pending_not_processing:
                    assert(!processing_internal);
                a_f_frame_bridge_pending_not_internal_drain:
                    assert(!draining_internal);
                a_f_frame_bridge_pending_not_abort:
                    assert(!frame_abort_q);
                a_f_frame_bridge_pending_no_metadata_error:
                    assert(!metadata_error_i);
            end

            if (raw_frame_done_internal) begin
                a_f_frame_bridge_raw_done_is_internal_drain:
                    assert(draining_internal);
                a_f_frame_bridge_raw_done_precedes_pending:
                    assert(!final_pending_q);
                a_f_frame_bridge_raw_done_precedes_output_final_tag:
                    assert(!(elastic_m_valid && elastic_m_data[10]));
            end
        end

        if (f_past_valid && !$past(rst) && !$past(metadata_error_i) &&
            $past(final_pending_q) && !$past(frame_done_external))
            a_f_frame_pending_holds_without_external_done: assert(final_pending_q);

        if (f_past_valid && !$past(rst) && !$past(metadata_error_i) &&
            $past(frame_done_external))
            a_f_frame_external_done_clears_pending: assert(!final_pending_q);

        if (f_past_valid && !$past(elastic_rst) &&
            $past(elastic_m_valid && elastic_m_data[10] && !m_tready))
            a_f_frame_final_tag_stable_while_stalled:
                assert(elastic_m_valid && elastic_m_data[10]);

        if (f_past_valid && frame_done_external && !rst) begin
            a_f_frame_external_done_requires_pending: assert(final_pending_q);
            a_f_frame_external_done_requires_tag:
                assert(elastic_m_valid && m_tready && elastic_m_data[10]);
        end

        if (f_past_valid && $past(frame_done_external) && !$past(rst))
            a_f_frame_external_done_single_pulse: assert(!frame_done_external);

        if (f_past_valid) begin
            if ($past(rst))
                a_f_frame_count_reset: assert(dut_frame_count_q == 32'd0);
            else if ($past(frame_done_external))
                a_f_frame_count_external_done_increment:
                    assert(dut_frame_count_q == $past(dut_frame_count_q) + 32'd1);
            else
                a_f_frame_count_no_external_done_stable:
                    assert(dut_frame_count_q == $past(dut_frame_count_q));
        end

        if (f_past_valid && !$past(rst) && dut_frame_count_q != $past(dut_frame_count_q))
            a_f_frame_count_change_requires_external_done:
                assert($past(frame_done_external));

        if (f_past_valid && !$past(rst) && $past(raw_frame_done_internal) &&
            !$past(frame_done_external))
            a_f_frame_internal_done_does_not_count:
                assert(dut_frame_count_q == $past(dut_frame_count_q));

        c_raw_internal_final: cover(f_past_valid && !rst && raw_frame_done_internal);
        c_final_pending_after_internal:
            cover(f_past_valid && $past(raw_frame_done_internal) && final_pending_q &&
                  elastic_m_valid && elastic_m_data[10]);
        c_final_external_stall:
            cover(f_past_valid && !rst && final_pending_q && elastic_m_valid &&
                  elastic_m_data[10] && !m_tready);
        c_final_stall_then_transfer:
            cover(f_past_valid && !$past(rst) &&
                  $past(final_pending_q && elastic_m_valid && elastic_m_data[10] && !m_tready) &&
                  frame_done_external);
        c_external_final_transfer: cover(f_past_valid && !rst && frame_done_external);
        c_frame_count_increment:
            cover(f_past_valid && !$past(rst) && $past(frame_done_external) &&
                  dut_frame_count_q == $past(dut_frame_count_q) + 32'd1);
        c_internal_final_without_count:
            cover(f_past_valid && !$past(rst) && $past(raw_frame_done_internal) &&
                  !$past(frame_done_external) && dut_frame_count_q == $past(dut_frame_count_q));
        c_pending_extends_draining_status:
            cover(f_past_valid && !rst && final_pending_q && !draining_internal && draining_status);
        c_pending_blocks_requested_input:
            cover(f_past_valid && !rst && final_pending_q && event_valid_i && !accepted_event);
        c_external_done_then_next_accept:
            cover(f_past_valid && !$past(rst) && $past(frame_done_external) &&
                  !final_pending_q && accepted_event);
    end
endmodule
