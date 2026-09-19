module window_3x3 #(
    parameter int unsigned DATA_WIDTH = 8,
    parameter int unsigned IMG_WIDTH  = 640,
    parameter int unsigned IMG_HEIGHT = 480
) (
    input  logic clk,
    input  logic rst,

    input  logic pixel_commit_i,
    input  logic frame_start_i,

    input  logic [$clog2(IMG_HEIGHT)-1:0] row_i,
    input  logic [$clog2(IMG_WIDTH)-1:0]  col_i,

    input  logic [DATA_WIDTH-1:0] pixel_i,

    input  logic [DATA_WIDTH-1:0] prev_row1_i,
    input  logic                  prev_row1_valid_i,

    input  logic [DATA_WIDTH-1:0] prev_row2_i,
    input  logic                  prev_row2_valid_i,

    output logic                  window_valid_o,

    output logic [$clog2(IMG_HEIGHT)-1:0] window_row_o,
    output logic [$clog2(IMG_WIDTH)-1:0]  window_col_o,

    output logic [DATA_WIDTH-1:0] p00_o,
    output logic [DATA_WIDTH-1:0] p01_o,
    output logic [DATA_WIDTH-1:0] p02_o,

    output logic [DATA_WIDTH-1:0] p10_o,
    output logic [DATA_WIDTH-1:0] p11_o,
    output logic [DATA_WIDTH-1:0] p12_o,

    output logic [DATA_WIDTH-1:0] p20_o,
    output logic [DATA_WIDTH-1:0] p21_o,
    output logic [DATA_WIDTH-1:0] p22_o
);

    localparam int unsigned ROW_W = $clog2(IMG_HEIGHT);
    localparam int unsigned COL_W = $clog2(IMG_WIDTH);

    logic [DATA_WIDTH-1:0] top_c2_q;
    logic [DATA_WIDTH-1:0] top_c1_q;

    logic [DATA_WIDTH-1:0] mid_c2_q;
    logic [DATA_WIDTH-1:0] mid_c1_q;

    logic [DATA_WIDTH-1:0] bot_c2_q;
    logic [DATA_WIDTH-1:0] bot_c1_q;

    always_comb begin
        window_valid_o =
            !rst &&
            pixel_commit_i &&
            prev_row1_valid_i &&
            prev_row2_valid_i &&
            (row_i >= ROW_W'(2)) &&
            (col_i >= COL_W'(2));

        window_row_o = '0;
        window_col_o = '0;

        p00_o = '0;
        p01_o = '0;
        p02_o = '0;

        p10_o = '0;
        p11_o = '0;
        p12_o = '0;

        p20_o = '0;
        p21_o = '0;
        p22_o = '0;

        if (window_valid_o) begin
            window_row_o = row_i - ROW_W'(1);
            window_col_o = col_i - COL_W'(1);

            p00_o = top_c2_q;
            p01_o = top_c1_q;
            p02_o = prev_row2_i;

            p10_o = mid_c2_q;
            p11_o = mid_c1_q;
            p12_o = prev_row1_i;

            p20_o = bot_c2_q;
            p21_o = bot_c1_q;
            p22_o = pixel_i;
        end
    end

    always_ff @(posedge clk) begin
        if (rst) begin
            top_c2_q <= '0;
            top_c1_q <= '0;

            mid_c2_q <= '0;
            mid_c1_q <= '0;

            bot_c2_q <= '0;
            bot_c1_q <= '0;
        end else if (pixel_commit_i) begin
            if (frame_start_i || (col_i == '0)) begin
                top_c2_q <= '0;
                top_c1_q <=
                    prev_row2_valid_i ? prev_row2_i : '0;

                mid_c2_q <= '0;
                mid_c1_q <=
                    prev_row1_valid_i ? prev_row1_i : '0;

                bot_c2_q <= '0;
                bot_c1_q <= pixel_i;
            end else begin
                top_c2_q <= top_c1_q;
                top_c1_q <=
                    prev_row2_valid_i ? prev_row2_i : '0;

                mid_c2_q <= mid_c1_q;
                mid_c1_q <=
                    prev_row1_valid_i ? prev_row1_i : '0;

                bot_c2_q <= bot_c1_q;
                bot_c1_q <= pixel_i;
            end
        end
    end

endmodule
