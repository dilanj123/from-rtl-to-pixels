module sobel_compact (
    input  logic [7:0] p00_i,
    input  logic [7:0] p01_i,
    input  logic [7:0] p02_i,

    input  logic [7:0] p10_i,
    input  logic [7:0] p12_i,

    input  logic [7:0] p20_i,
    input  logic [7:0] p21_i,
    input  logic [7:0] p22_i,

    output logic signed [11:0] gx_o,
    output logic signed [11:0] gy_o
);

    logic signed [11:0] p00_s;
    logic signed [11:0] p01_s;
    logic signed [11:0] p02_s;

    logic signed [11:0] p10_s;
    logic signed [11:0] p12_s;

    logic signed [11:0] p20_s;
    logic signed [11:0] p21_s;
    logic signed [11:0] p22_s;

    always_comb begin
        p00_s = $signed({4'b0000, p00_i});
        p01_s = $signed({4'b0000, p01_i});
        p02_s = $signed({4'b0000, p02_i});

        p10_s = $signed({4'b0000, p10_i});
        p12_s = $signed({4'b0000, p12_i});

        p20_s = $signed({4'b0000, p20_i});
        p21_s = $signed({4'b0000, p21_i});
        p22_s = $signed({4'b0000, p22_i});

        gx_o =
            -p00_s
            + p02_s
            - (p10_s <<< 1)
            + (p12_s <<< 1)
            - p20_s
            + p22_s;

        gy_o =
            -p00_s
            - (p01_s <<< 1)
            - p02_s
            + p20_s
            + (p21_s <<< 1)
            + p22_s;
    end

endmodule
