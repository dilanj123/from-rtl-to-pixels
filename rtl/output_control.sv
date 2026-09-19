module output_control #(
    parameter int unsigned IMG_WIDTH  = 640,
    parameter int unsigned IMG_HEIGHT = 480
) (
    input  logic clk,
    input  logic rst,

    input  logic pixel_commit_i,
    input  logic frame_start_i,
    input  logic last_input_accept_i,
    input  logic frame_abort_i,

    input  logic output_ready_i,

    output logic input_allow_o,

    output logic output_valid_o,
    output logic [$clog2(IMG_HEIGHT)-1:0] output_row_o,
    output logic [$clog2(IMG_WIDTH)-1:0]  output_col_o,
    output logic output_border_o,

    output logic processing_o,
    output logic draining_o,
    output logic waiting_for_sof_o,

    output logic frame_done_o
);

    localparam int unsigned ROW_W =
        $clog2(IMG_HEIGHT);

    localparam int unsigned COL_W =
        $clog2(IMG_WIDTH);

    localparam int unsigned FRAME_PIXELS =
        IMG_WIDTH * IMG_HEIGHT;

    localparam int unsigned COUNT_W =
        $clog2(FRAME_PIXELS + 1);

    localparam logic [ROW_W-1:0] LAST_ROW =
        ROW_W'(IMG_HEIGHT - 1);

    localparam logic [COL_W-1:0] LAST_COL =
        COL_W'(IMG_WIDTH - 1);

    localparam logic [COUNT_W-1:0] LIVE_START_COUNT =
        COUNT_W'(IMG_WIDTH + 1);

    typedef enum logic [1:0] {
        WAIT_SOF,
        PROCESS,
        DRAIN
    } state_t;

    state_t state_q;

    logic [COUNT_W-1:0] input_count_q;

    logic [ROW_W-1:0] output_row_q;
    logic [COL_W-1:0] output_col_q;

    logic live_output_due;
    logic final_output_position;

    assign processing_o =
        (state_q == PROCESS);

    assign draining_o =
        (state_q == DRAIN);

    assign waiting_for_sof_o =
        (state_q == WAIT_SOF);

    assign live_output_due =
        (state_q == PROCESS) &&
        (input_count_q >= LIVE_START_COUNT);

    assign final_output_position =
        (output_row_q == LAST_ROW) &&
        (output_col_q == LAST_COL);

    always_comb begin
        input_allow_o = 1'b0;

        if (!rst && !frame_abort_i) begin
            case (state_q)
                WAIT_SOF: begin
                    input_allow_o = 1'b1;
                end

                PROCESS: begin
                    if (live_output_due) begin
                        input_allow_o = output_ready_i;
                    end else begin
                        input_allow_o = 1'b1;
                    end
                end

                DRAIN: begin
                    input_allow_o = 1'b0;
                end

                default: begin
                    input_allow_o = 1'b0;
                end
            endcase
        end
    end

    always_comb begin
        output_valid_o  = 1'b0;
        output_row_o    = '0;
        output_col_o    = '0;
        output_border_o = 1'b0;
        frame_done_o    = 1'b0;

        if (!rst && !frame_abort_i) begin
            if (
                (state_q == PROCESS) &&
                live_output_due &&
                pixel_commit_i
            ) begin
                output_valid_o = 1'b1;
            end else if (state_q == DRAIN) begin
                output_valid_o = 1'b1;
            end

            if (output_valid_o) begin
                output_row_o = output_row_q;
                output_col_o = output_col_q;

                output_border_o =
                    (output_row_q == '0) ||
                    (output_row_q == LAST_ROW) ||
                    (output_col_q == '0) ||
                    (output_col_q == LAST_COL);
            end

            frame_done_o =
                (state_q == DRAIN) &&
                output_valid_o &&
                output_ready_i &&
                final_output_position;
        end
    end

    always_ff @(posedge clk) begin
        if (rst) begin
            state_q       <= WAIT_SOF;
            input_count_q <= '0;

            output_row_q <= '0;
            output_col_q <= '0;
        end else if (frame_abort_i) begin
            state_q       <= WAIT_SOF;
            input_count_q <= '0;

            output_row_q <= '0;
            output_col_q <= '0;
        end else begin
            case (state_q)
                WAIT_SOF: begin
                    input_count_q <= '0;
                    output_row_q  <= '0;
                    output_col_q  <= '0;

                    if (pixel_commit_i && frame_start_i) begin
                        state_q       <= PROCESS;
                        input_count_q <= COUNT_W'(1);
                    end
                end

                PROCESS: begin
                    if (pixel_commit_i) begin
                        if (live_output_due) begin
                            if (output_col_q == LAST_COL) begin
                                output_col_q <= '0;
                                output_row_q <=
                                    output_row_q + ROW_W'(1);
                            end else begin
                                output_col_q <=
                                    output_col_q + COL_W'(1);
                            end
                        end

                        input_count_q <=
                            input_count_q + COUNT_W'(1);

                        if (last_input_accept_i) begin
                            state_q <= DRAIN;
                        end
                    end
                end

                DRAIN: begin
                    if (output_ready_i) begin
                        if (final_output_position) begin
                            state_q       <= WAIT_SOF;
                            input_count_q <= '0;

                            output_row_q <= '0;
                            output_col_q <= '0;
                        end else if (output_col_q == LAST_COL) begin
                            output_col_q <= '0;
                            output_row_q <=
                                output_row_q + ROW_W'(1);
                        end else begin
                            output_col_q <=
                                output_col_q + COL_W'(1);
                        end
                    end
                end

                default: begin
                    state_q       <= WAIT_SOF;
                    input_count_q <= '0;

                    output_row_q <= '0;
                    output_col_q <= '0;
                end
            endcase
        end
    end

endmodule
