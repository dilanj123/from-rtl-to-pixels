module line_buffer #(
    parameter int unsigned DATA_WIDTH = 8,
    parameter int unsigned IMG_WIDTH  = 640
) (
    input  logic clk,
    input  logic rst,

    input  logic pixel_commit_i,
    input  logic frame_start_i,
    input  logic [$clog2(IMG_WIDTH)-1:0] col_i,
    input  logic [DATA_WIDTH-1:0] pixel_i,

    output logic [DATA_WIDTH-1:0] prev_row1_o,
    output logic                  prev_row1_valid_o,

    output logic [DATA_WIDTH-1:0] prev_row2_o,
    output logic                  prev_row2_valid_o
);

    localparam int unsigned COL_W = $clog2(IMG_WIDTH);

    localparam logic [COL_W-1:0] LAST_COL =
        COL_W'(IMG_WIDTH - 1);

    logic [DATA_WIDTH-1:0] line1_mem [0:IMG_WIDTH-1];
    logic [DATA_WIDTH-1:0] line2_mem [0:IMG_WIDTH-1];

    logic [1:0] history_rows_q;

    always_comb begin
        prev_row1_valid_o =
            !rst &&
            pixel_commit_i &&
            !frame_start_i &&
            (history_rows_q >= 2'd1);

        prev_row2_valid_o =
            !rst &&
            pixel_commit_i &&
            !frame_start_i &&
            (history_rows_q >= 2'd2);

        prev_row1_o = '0;
        prev_row2_o = '0;

        if (prev_row1_valid_o) begin
            prev_row1_o = line1_mem[col_i];
        end

        if (prev_row2_valid_o) begin
            prev_row2_o = line2_mem[col_i];
        end
    end

    always_ff @(posedge clk) begin
        if (rst) begin
            history_rows_q <= 2'd0;
        end else begin
            if (frame_start_i) begin
                history_rows_q <= 2'd0;
            end else if (
                pixel_commit_i &&
                (col_i == LAST_COL) &&
                (history_rows_q < 2'd2)
            ) begin
                history_rows_q <= history_rows_q + 2'd1;
            end

            if (pixel_commit_i) begin
                line2_mem[col_i] <= line1_mem[col_i];
                line1_mem[col_i] <= pixel_i;
            end
        end
    end

endmodule
