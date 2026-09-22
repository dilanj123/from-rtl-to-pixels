module elastic_stage #(
    parameter int unsigned DATA_WIDTH = 8
) (
    input  logic                  clk,
    input  logic                  rst,

    input  logic [DATA_WIDTH-1:0] s_data,
    input  logic                  s_valid,
    output logic                  s_ready,

    output logic [DATA_WIDTH-1:0] m_data,
    output logic                  m_valid,
    input  logic                  m_ready
);

    logic [DATA_WIDTH-1:0] data_q;
    logic                  valid_q;

    assign s_ready = !valid_q || m_ready;
    assign m_data  = s_valid ? s_data : data_q;
    assign m_valid = valid_q;

    always_ff @(posedge clk) begin
        if (rst) begin
            valid_q <= 1'b0;
        end else if (s_ready) begin
            valid_q <= s_valid;

            if (s_valid) begin
                data_q <= s_data;
            end
        end
    end

endmodule
