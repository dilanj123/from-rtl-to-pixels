module apb_regs_formal (
    input logic clk
);

    localparam logic [7:0] ADDR_CONTROL     = 8'h00;
    localparam logic [7:0] ADDR_THRESHOLD   = 8'h04;
    localparam logic [7:0] ADDR_STATUS      = 8'h08;
    localparam logic [7:0] ADDR_FRAME_COUNT = 8'h0C;

    (* anyseq *) logic        rst;
    (* anyseq *) logic        psel;
    (* anyseq *) logic        penable;
    (* anyseq *) logic        pwrite;
    (* anyseq *) logic [7:0]  paddr;
    (* anyseq *) logic [31:0] pwdata;
    (* anyseq *) logic processing_i;
    (* anyseq *) logic draining_i;
    (* anyseq *) logic sof_accept_i;
    (* anyseq *) logic frame_error_set_i;
    (* anyseq *) logic frame_done_i;

    logic [31:0] prdata;
    logic pready;
    logic pslverr;
    logic run_enable_o;
    logic [7:0] threshold_active_o;
    logic bypass_threshold_active_o;

    logic [7:0] dut_threshold_shadow_q;
    logic       dut_bypass_threshold_shadow_q;
    logic       dut_frame_error_q;
    logic [31:0] dut_frame_count_q;

    logic f_past_valid = 1'b0;
    logic f_run_enable = 1'b0;
    logic [7:0] f_threshold_shadow = 8'd128;
    logic [7:0] f_threshold_active = 8'd128;
    logic f_bypass_shadow = 1'b0;
    logic f_bypass_active = 1'b0;
    logic f_frame_error = 1'b0;
    logic [31:0] f_frame_count = 32'd0;
    logic f_addr_valid;
    logic f_write_access;
    logic f_status_w1c_error;
    logic f_config_pending;

    assign f_addr_valid =
        (paddr == ADDR_CONTROL) ||
        (paddr == ADDR_THRESHOLD) ||
        (paddr == ADDR_STATUS) ||
        (paddr == ADDR_FRAME_COUNT);

    assign f_write_access = psel && penable && pwrite && f_addr_valid;
    assign f_status_w1c_error = f_write_access &&
        (paddr == ADDR_STATUS) && pwdata[3];
    assign f_config_pending =
        (f_threshold_shadow != f_threshold_active) ||
        (f_bypass_shadow != f_bypass_active);

    apb_regs dut (
        .clk                         (clk),
        .rst                         (rst),
        .psel                        (psel),
        .penable                     (penable),
        .pwrite                      (pwrite),
        .paddr                       (paddr),
        .pwdata                      (pwdata),
        .prdata                      (prdata),
        .pready                      (pready),
        .pslverr                     (pslverr),
        .processing_i                (processing_i),
        .draining_i                  (draining_i),
        .sof_accept_i                (sof_accept_i),
        .frame_error_set_i           (frame_error_set_i),
        .frame_done_i                (frame_done_i),
        .run_enable_o                (run_enable_o),
        .threshold_active_o          (threshold_active_o),
        .bypass_threshold_active_o   (bypass_threshold_active_o),
        .threshold_shadow_q          (dut_threshold_shadow_q),
        .bypass_threshold_shadow_q   (dut_bypass_threshold_shadow_q),
        .frame_error_q               (dut_frame_error_q),
        .frame_count_q               (dut_frame_count_q)
    );

    always_ff @(posedge clk) begin
        /* Explicit inductive correspondence between the architectural
         * ghost state and the production block's hidden state. */
        if (f_past_valid) begin
            a_f_apb_state_run_enable_matches:
                assert(run_enable_o == f_run_enable);
            a_f_apb_state_threshold_shadow_matches:
                assert(dut_threshold_shadow_q == f_threshold_shadow);
            a_f_apb_state_threshold_active_matches:
                assert(threshold_active_o == f_threshold_active);
            a_f_apb_state_bypass_shadow_matches:
                assert(dut_bypass_threshold_shadow_q == f_bypass_shadow);
            a_f_apb_state_bypass_active_matches:
                assert(bypass_threshold_active_o == f_bypass_active);
            a_f_apb_state_frame_error_matches:
                assert(dut_frame_error_q == f_frame_error);
            a_f_apb_state_frame_count_matches:
                assert(dut_frame_count_q == f_frame_count);
        end

        if (!f_past_valid) begin
            assume(rst);
        end
        f_past_valid <= 1'b1;

        if (f_past_valid) begin
            a_f_apb_001_pready: assert(pready);
            a_f_apb_001_pslverr: assert(
                pslverr == (psel && penable && !f_addr_valid)
            );
            a_f_apb_001_run_enable_state: assert(run_enable_o == f_run_enable);
            a_f_apb_001_threshold_active_state: assert(
                threshold_active_o == f_threshold_active
            );
            a_f_apb_001_bypass_active_state: assert(
                bypass_threshold_active_o == f_bypass_active
            );

            case (paddr)
                ADDR_CONTROL: begin
                    a_f_apb_001_control_read: assert(
                        prdata == {30'd0, f_bypass_shadow, f_run_enable}
                    );
                end
                ADDR_THRESHOLD: begin
                    a_f_apb_001_threshold_read: assert(
                        prdata == {24'd0, f_threshold_shadow}
                    );
                end
                ADDR_STATUS: begin
                    a_f_apb_001_status_read: assert(
                        prdata == {28'd0, f_frame_error, f_config_pending,
                                   draining_i, (processing_i || draining_i)}
                    );
                end
                ADDR_FRAME_COUNT: begin
                    a_f_apb_001_frame_count_read: assert(
                        prdata == f_frame_count
                    );
                end
                default: begin
                    a_f_apb_001_invalid_read_zero: assert(prdata == 32'd0);
                end
            endcase

            if (psel && penable && f_addr_valid) begin
                a_f_apb_001_valid_access_no_error: assert(!pslverr);
            end
            if (psel && penable && !f_addr_valid) begin
                a_f_apb_001_invalid_access_error: assert(pslverr);
                a_f_apb_001_invalid_access_zero_read: assert(prdata == 32'd0);
            end
        end

        if (f_past_valid) begin
            if ($past(rst)) begin
                a_f_apb_001_reset_run_enable: assert(run_enable_o == 1'b0);
                a_f_apb_001_reset_threshold_active: assert(
                    threshold_active_o == 8'd128
                );
                a_f_apb_001_reset_bypass_active: assert(
                    bypass_threshold_active_o == 1'b0
                );
            end else begin
                if ($past(f_write_access && (paddr == ADDR_CONTROL))) begin
                    a_f_apb_001_control_write: assert(
                        run_enable_o == $past(pwdata[0])
                    );
                end else begin
                    a_f_apb_001_run_enable_stable: assert(
                        run_enable_o == $past(run_enable_o)
                    );
                end

                if ($past(frame_done_i)) begin
                    a_f_apb_001_frame_count_increment: assert(
                        f_frame_count == ($past(f_frame_count) + 32'd1)
                    );
                end else begin
                    a_f_apb_001_frame_count_stable: assert(
                        f_frame_count == $past(f_frame_count)
                    );
                end

                if ($past(frame_error_set_i)) begin
                    a_f_apb_001_frame_error_set_wins: assert(f_frame_error);
                end else if ($past(f_status_w1c_error)) begin
                    a_f_apb_001_frame_error_w1c: assert(!f_frame_error);
                end else begin
                    a_f_apb_001_frame_error_sticky: assert(
                        f_frame_error == $past(f_frame_error)
                    );
                end
            end
        end

        if (f_past_valid && !$past(rst)) begin
            if ($past(sof_accept_i)) begin
                a_f_apb_002_threshold_sof_activates_preedge_shadow: assert(
                    threshold_active_o == $past(f_threshold_shadow)
                );
                a_f_apb_002_bypass_sof_activates_preedge_shadow: assert(
                    bypass_threshold_active_o == $past(f_bypass_shadow)
                );
            end else begin
                a_f_apb_002_threshold_active_stable_without_sof: assert(
                    threshold_active_o == $past(threshold_active_o)
                );
                a_f_apb_002_bypass_active_stable_without_sof: assert(
                    bypass_threshold_active_o == $past(bypass_threshold_active_o)
                );
            end

            if ($past(f_write_access && (paddr == ADDR_THRESHOLD) && sof_accept_i)) begin
                a_f_apb_002_same_edge_threshold_priority: assert(
                    threshold_active_o == $past(f_threshold_shadow)
                );
                a_f_apb_002_same_edge_threshold_new_shadow: assert(
                    f_threshold_shadow == $past(pwdata[7:0])
                );
            end
            if ($past(f_write_access && (paddr == ADDR_CONTROL) && sof_accept_i)) begin
                a_f_apb_002_same_edge_bypass_priority: assert(
                    bypass_threshold_active_o == $past(f_bypass_shadow)
                );
                a_f_apb_002_same_edge_bypass_new_shadow: assert(
                    f_bypass_shadow == $past(pwdata[1])
                );
            end
        end

        c_valid_control_write: cover(
            f_past_valid && !rst && f_write_access && paddr == ADDR_CONTROL
        );
        c_valid_threshold_write: cover(
            f_past_valid && !rst && f_write_access && paddr == ADDR_THRESHOLD
        );
        c_invalid_read: cover(
            f_past_valid && !rst && psel && penable && !pwrite &&
            !f_addr_valid && pslverr && prdata == 32'd0
        );
        c_invalid_write: cover(
            f_past_valid && !rst && psel && penable && pwrite &&
            !f_addr_valid && pslverr
        );
        c_frame_error_w1c: cover(
            f_past_valid && !rst && f_frame_error &&
            f_status_w1c_error && !frame_error_set_i
        );
        c_frame_error_set_and_w1c_same_edge: cover(
            f_past_valid && !rst && frame_error_set_i && f_status_w1c_error
        );
        c_same_edge_threshold_write_sof: cover(
            f_past_valid && !rst && f_write_access &&
            paddr == ADDR_THRESHOLD && sof_accept_i &&
            pwdata[7:0] != f_threshold_shadow
        );
        c_same_edge_bypass_write_sof: cover(
            f_past_valid && !rst && f_write_access &&
            paddr == ADDR_CONTROL && sof_accept_i &&
            pwdata[1] != f_bypass_shadow
        );
        c_config_pending: cover(
            f_past_valid && !rst && f_config_pending
        );
        c_config_pending_cleared_by_sof: cover(
            f_past_valid && !rst && !$past(rst) &&
            $past(f_config_pending && sof_accept_i &&
                  !(f_write_access &&
                    (paddr == ADDR_CONTROL || paddr == ADDR_THRESHOLD))) &&
            !f_config_pending
        );

        if (rst) begin
            f_run_enable <= 1'b0;
            f_threshold_shadow <= 8'd128;
            f_threshold_active <= 8'd128;
            f_bypass_shadow <= 1'b0;
            f_bypass_active <= 1'b0;
            f_frame_error <= 1'b0;
            f_frame_count <= 32'd0;
        end else begin
            if (f_write_access && paddr == ADDR_CONTROL) begin
                f_run_enable <= pwdata[0];
                f_bypass_shadow <= pwdata[1];
            end
            if (f_write_access && paddr == ADDR_THRESHOLD) begin
                f_threshold_shadow <= pwdata[7:0];
            end
            if (sof_accept_i) begin
                f_threshold_active <= f_threshold_shadow;
                f_bypass_active <= f_bypass_shadow;
            end
            if (frame_error_set_i) begin
                f_frame_error <= 1'b1;
            end else if (f_status_w1c_error) begin
                f_frame_error <= 1'b0;
            end
            if (frame_done_i) begin
                f_frame_count <= f_frame_count + 32'd1;
            end
        end
    end

endmodule
