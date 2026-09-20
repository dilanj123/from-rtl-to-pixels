module formal_toolchain_smoke (
    input logic clk
);

    logic [2:0] counter = 3'd0;
    logic       past_valid = 1'b0;

    always_ff @(posedge clk) begin
        past_valid <= 1'b1;
        counter    <= counter + 3'd1;

        if (past_valid) begin
            assert (
                counter ==
                ($past(counter) + 3'd1)
            );
        end

        cover (
            past_valid &&
            counter == 3'd5
        );
    end

endmodule
