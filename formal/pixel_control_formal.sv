module pixel_control_formal #(
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
    (* anyseq *) logic accept_i;
    (* anyseq *) logic s_tuser_i;
    (* anyseq *) logic s_tlast_i;

    logic [ROW_W-1:0] row_o;
    logic [COL_W-1:0] col_o;
    logic pixel_commit_o;
    logic sof_accept_o;
    logic last_input_accept_o;
    logic metadata_error_o;
    logic waiting_for_sof_o;

    logic f_past_valid = 1'b0;
    logic f_expected_sof;
    logic f_expected_eol;
    logic f_metadata_ok;

    assign f_expected_sof = waiting_for_sof_o;
    assign f_expected_eol = (col_o == LAST_COL);
    assign f_metadata_ok =
        (s_tuser_i == f_expected_sof) &&
        (s_tlast_i == f_expected_eol);

    pixel_control #(
        .IMG_WIDTH  (IMG_WIDTH),
        .IMG_HEIGHT (IMG_HEIGHT)
    ) dut (
        .clk                 (clk),
        .rst                 (rst),
        .accept_i            (accept_i),
        .s_tuser_i           (s_tuser_i),
        .s_tlast_i           (s_tlast_i),
        .row_o               (row_o),
        .col_o               (col_o),
        .pixel_commit_o      (pixel_commit_o),
        .sof_accept_o        (sof_accept_o),
        .last_input_accept_o (last_input_accept_o),
        .metadata_error_o    (metadata_error_o),
        .waiting_for_sof_o   (waiting_for_sof_o)
    );

    always_ff @(posedge clk) begin
        if (!f_past_valid) begin
            assume(rst);
        end
        f_past_valid <= 1'b1;

        if (f_past_valid) begin
            a_f_ctrl_001_row_legal: assert(row_o <= LAST_ROW);
            a_f_ctrl_001_col_legal: assert(col_o <= LAST_COL);

            if (waiting_for_sof_o) begin
                a_f_ctrl_001_wait_row_zero: assert(row_o == ROW_W'(0));
                a_f_ctrl_001_wait_col_zero: assert(col_o == COL_W'(0));
            end

            if (!waiting_for_sof_o) begin
                a_f_ctrl_001_in_frame_not_origin: assert(
                    !(row_o == ROW_W'(0) && col_o == COL_W'(0))
                );
            end

            a_f_ctrl_001_commit_definition: assert(
                pixel_commit_o == (!rst && accept_i && f_metadata_ok)
            );
            a_f_ctrl_001_sof_definition: assert(
                sof_accept_o == (pixel_commit_o && waiting_for_sof_o)
            );
            a_f_ctrl_001_last_definition: assert(
                last_input_accept_o ==
                (pixel_commit_o && row_o == LAST_ROW && col_o == LAST_COL)
            );
            a_f_ctrl_001_error_definition: assert(
                metadata_error_o == (!rst && accept_i && !f_metadata_ok)
            );
            a_f_ctrl_001_commit_error_exclusive: assert(
                !(pixel_commit_o && metadata_error_o)
            );

            if (sof_accept_o) begin
                a_f_ctrl_001_sof_origin: assert(
                    row_o == ROW_W'(0) && col_o == COL_W'(0) &&
                    s_tuser_i && !s_tlast_i
                );
            end

            if (last_input_accept_o) begin
                a_f_ctrl_001_last_metadata: assert(
                    row_o == LAST_ROW && col_o == LAST_COL &&
                    !s_tuser_i && s_tlast_i
                );
            end
        end

        if (f_past_valid) begin
            if ($past(rst)) begin
                a_f_ctrl_001_reset_wait: assert(waiting_for_sof_o);
                a_f_ctrl_001_reset_row: assert(row_o == ROW_W'(0));
                a_f_ctrl_001_reset_col: assert(col_o == COL_W'(0));
            end else if (!$past(accept_i)) begin
                a_f_ctrl_001_no_accept_wait_hold: assert(
                    waiting_for_sof_o == $past(waiting_for_sof_o)
                );
                a_f_ctrl_001_no_accept_row_hold: assert(row_o == $past(row_o));
                a_f_ctrl_001_no_accept_col_hold: assert(col_o == $past(col_o));
            end else if (!$past(f_metadata_ok)) begin
                a_f_ctrl_001_bad_metadata_wait: assert(waiting_for_sof_o);
                a_f_ctrl_001_bad_metadata_row: assert(row_o == ROW_W'(0));
                a_f_ctrl_001_bad_metadata_col: assert(col_o == COL_W'(0));
            end else if ($past(waiting_for_sof_o)) begin
                a_f_ctrl_001_sof_enters_frame: assert(!waiting_for_sof_o);
                a_f_ctrl_001_sof_row: assert(row_o == ROW_W'(0));
                a_f_ctrl_001_sof_next_col: assert(col_o == COL_W'(1));
            end else if ($past(col_o == LAST_COL)) begin
                if ($past(row_o == LAST_ROW)) begin
                    a_f_ctrl_001_final_returns_wait: assert(waiting_for_sof_o);
                    a_f_ctrl_001_final_row_zero: assert(row_o == ROW_W'(0));
                    a_f_ctrl_001_final_col_zero: assert(col_o == COL_W'(0));
                end else begin
                    a_f_ctrl_001_eol_stays_frame: assert(!waiting_for_sof_o);
                    a_f_ctrl_001_eol_next_row: assert(
                        row_o == ($past(row_o) + ROW_W'(1))
                    );
                    a_f_ctrl_001_eol_col_zero: assert(col_o == COL_W'(0));
                end
            end else begin
                a_f_ctrl_001_inner_stays_frame: assert(!waiting_for_sof_o);
                a_f_ctrl_001_inner_row_hold: assert(row_o == $past(row_o));
                a_f_ctrl_001_inner_col_increment: assert(
                    col_o == ($past(col_o) + COL_W'(1))
                );
            end
        end

        c_valid_sof_accept: cover(
            f_past_valid && !rst && accept_i && waiting_for_sof_o &&
            s_tuser_i && !s_tlast_i && pixel_commit_o && sof_accept_o
        );
        c_interior_accept: cover(
            f_past_valid && !rst && accept_i && !waiting_for_sof_o &&
            col_o != LAST_COL && f_metadata_ok && pixel_commit_o
        );
        c_row_eol_accept: cover(
            f_past_valid && !rst && accept_i && !waiting_for_sof_o &&
            row_o != LAST_ROW && col_o == LAST_COL && f_metadata_ok &&
            pixel_commit_o
        );
        c_last_pixel_accept: cover(
            f_past_valid && !rst && accept_i && !waiting_for_sof_o &&
            row_o == LAST_ROW && col_o == LAST_COL && f_metadata_ok &&
            pixel_commit_o && last_input_accept_o
        );
        c_missing_sof_error: cover(
            f_past_valid && !rst && accept_i && waiting_for_sof_o &&
            !s_tuser_i && metadata_error_o
        );
        c_unexpected_sof_error: cover(
            f_past_valid && !rst && accept_i && !waiting_for_sof_o &&
            s_tuser_i && metadata_error_o
        );
        c_premature_eol_error: cover(
            f_past_valid && !rst && accept_i && !waiting_for_sof_o &&
            col_o != LAST_COL && s_tlast_i && metadata_error_o
        );
        c_missing_eol_error: cover(
            f_past_valid && !rst && accept_i && !waiting_for_sof_o &&
            col_o == LAST_COL && !s_tlast_i && metadata_error_o
        );
        c_nonaccept_hold: cover(
            f_past_valid && !$past(rst) && !$past(accept_i) &&
            row_o == $past(row_o) && col_o == $past(col_o) &&
            waiting_for_sof_o == $past(waiting_for_sof_o)
        );
        c_reset_midframe_recovery: cover(
            f_past_valid && $past(rst && !waiting_for_sof_o) &&
            waiting_for_sof_o && row_o == ROW_W'(0) && col_o == COL_W'(0)
        );
    end
endmodule
