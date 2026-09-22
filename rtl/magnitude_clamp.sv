module magnitude_clamp (
    input  logic [11:0] gx_i,
    input logic [11:0] gy_i,
    output logic [10:0] magnitude_o,
    output logic [7:0]  magnitude_clamped_o
);
    logic [10:0] abs_gx;
    logic [10:0] abs_gy;
    logic [10:0] magnitude_sum;

    always_comb begin
        // The valid Sobel input contract is -1020..+1020.
        // For a negative two's-complement 12-bit input in that range,
        // taking two's complement over the lower 11 bits produces the
        // exact positive magnitude because abs(input) <= 1020.
        // This avoids a redundant 12-bit negation temporary whose top
        // bit would be provably unused under the valid input contract.
        if (gx_i < 12'sd0) begin
            abs_gx = (~gx_i[10:0]) + 11'd1;
        end else begin
            abs_gx = gx_i[10:0];
        end
        if (gy_i < 12'sd0) begin
            abs_gy = (~gy_i[10:0]) + 11'd1;
        end else begin
            abs_gy = gy_i[10:0];
        end
        magnitude_sum = abs_gx + abs_gy;
        magnitude_o = magnitude_sum;
        if (magnitude_sum > 11'd255) begin
            magnitude_clamped_o = 8'hff;
        end else begin
            magnitude_clamped_o = magnitude_sum[7:0];
        end
    end
endmodule
