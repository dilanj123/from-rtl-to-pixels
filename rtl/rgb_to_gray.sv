module rgb_to_gray (
    input  pixel_pkg::rgb888_t   rgb_i,
    output pixel_pkg::pixel_u8_t gray_o
);

    logic [15:0] r_ext;
    logic [15:0] g_ext;
    logic [15:0] b_ext;
    logic [15:0] accum;

    always_comb begin
        r_ext = {8'b0, rgb_i[23:16]};
        g_ext = {8'b0, rgb_i[15:8]};
        b_ext = {8'b0, rgb_i[7:0]};

        accum =
            (16'd77  * r_ext) +
            (16'd150 * g_ext) +
            (16'd29  * b_ext) +
            16'd128;

        gray_o = pixel_pkg::pixel_u8_t'(accum >> 8);
    end

endmodule
