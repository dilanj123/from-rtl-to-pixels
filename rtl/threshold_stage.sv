module threshold_stage (
    input  logic [7:0] magnitude_i,
    input  logic [7:0] threshold_i,
    input  logic       bypass_threshold_i,

    output logic [7:0] edge_o
);

    always_comb begin
        if (bypass_threshold_i) begin
            edge_o = magnitude_i;
        end else if (magnitude_i < threshold_i) begin
            edge_o = 8'd0;
        end else begin
            edge_o = magnitude_i;
        end
    end

endmodule
