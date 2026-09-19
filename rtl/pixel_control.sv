module pixel_control #(
    parameter int unsigned IMG_WIDTH  = 640,
    parameter int unsigned IMG_HEIGHT = 480
) (
    input  logic clk,
    input  logic rst,

    input  logic accept_i,
    input  logic s_tuser_i,
    input  logic s_tlast_i,

    output logic [$clog2(IMG_HEIGHT)-1:0] row_o,
    output logic [$clog2(IMG_WIDTH)-1:0]  col_o,

    output logic pixel_commit_o,
    output logic sof_accept_o,
    output logic last_input_accept_o,
    output logic metadata_error_o,
    output logic waiting_for_sof_o
);

    localparam int unsigned ROW_W = $clog2(IMG_HEIGHT);
    localparam int unsigned COL_W = $clog2(IMG_WIDTH);

    localparam logic [ROW_W-1:0] LAST_ROW =
        ROW_W'(IMG_HEIGHT - 1);

    localparam logic [COL_W-1:0] LAST_COL =
        COL_W'(IMG_WIDTH - 1);

    typedef enum logic {
        WAIT_SOF,
        IN_FRAME
    } state_t;

    state_t state_q;

    logic [ROW_W-1:0] row_q;
    logic [COL_W-1:0] col_q;

    logic expected_sof;
    logic expected_eol;
    logic metadata_ok;

    assign row_o = row_q;
    assign col_o = col_q;

    assign waiting_for_sof_o = (state_q == WAIT_SOF);

    assign expected_sof = (state_q == WAIT_SOF);
    assign expected_eol = (col_q == LAST_COL);

    assign metadata_ok =
        (s_tuser_i == expected_sof) &&
        (s_tlast_i == expected_eol);

    always_comb begin
        pixel_commit_o      = 1'b0;
        sof_accept_o        = 1'b0;
        last_input_accept_o = 1'b0;
        metadata_error_o    = 1'b0;

        if (!rst && accept_i) begin
            if (metadata_ok) begin
                pixel_commit_o = 1'b1;
                sof_accept_o   = expected_sof;

                last_input_accept_o =
                    (row_q == LAST_ROW) &&
                    (col_q == LAST_COL);
            end else begin
                metadata_error_o = 1'b1;
            end
        end
    end

    always_ff @(posedge clk) begin
        if (rst) begin
            state_q <= WAIT_SOF;
            row_q   <= '0;
            col_q   <= '0;
        end else if (accept_i) begin
            if (!metadata_ok) begin
                state_q <= WAIT_SOF;
                row_q   <= '0;
                col_q   <= '0;
            end else if (state_q == WAIT_SOF) begin
                state_q <= IN_FRAME;
                row_q   <= '0;
                col_q   <= COL_W'(1);
            end else if (col_q == LAST_COL) begin
                if (row_q == LAST_ROW) begin
                    state_q <= WAIT_SOF;
                    row_q   <= '0;
                    col_q   <= '0;
                end else begin
                    row_q <= row_q + ROW_W'(1);
                    col_q <= '0;
                end
            end else begin
                col_q <= col_q + COL_W'(1);
            end
        end
    end

endmodule
