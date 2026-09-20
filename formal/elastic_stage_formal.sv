module elastic_stage_formal #(
    parameter int unsigned DATA_WIDTH = 11
) (
    input logic clk
);

    (* anyseq *) logic                  rst;
    (* anyseq *) logic [DATA_WIDTH-1:0] s_data;
    (* anyseq *) logic                  s_valid;
    (* anyseq *) logic                  m_ready;

    logic                  s_ready;
    logic [DATA_WIDTH-1:0] m_data;
    logic                  m_valid;

    logic                  f_past_valid = 1'b0;
    logic [1:0]            f_occupancy = 2'd0;
    logic [DATA_WIDTH-1:0] f_token_data = '0;

    logic f_in_fire;
    logic f_out_fire;

    assign f_in_fire  = s_valid && s_ready;
    assign f_out_fire = m_valid && m_ready;

    elastic_stage #(
        .DATA_WIDTH(DATA_WIDTH)
    ) dut (
        .clk     (clk),
        .rst     (rst),
        .s_data  (s_data),
        .s_valid (s_valid),
        .s_ready (s_ready),
        .m_data  (m_data),
        .m_valid (m_valid),
        .m_ready (m_ready)
    );

    always_ff @(posedge clk) begin
        if (!f_past_valid) begin
            assume(rst);
        end

        f_past_valid <= 1'b1;

        if (rst) begin
            f_occupancy <= 2'd0;
            f_token_data <= '0;
        end else begin
            case ({f_in_fire, f_out_fire})
                2'b10: f_occupancy <= f_occupancy + 2'd1;
                2'b01: f_occupancy <= f_occupancy - 2'd1;
                default: f_occupancy <= f_occupancy;
            endcase

            if (f_in_fire) begin
                f_token_data <= s_data;
            end
        end

        if (f_past_valid && !rst && !$past(rst) &&
            $past(m_valid && !m_ready)) begin
            a_f_elastic_001_valid_stable: assert(m_valid);
            a_f_elastic_001_data_stable: assert(m_data == $past(m_data));
        end

        if (f_past_valid && !rst && m_valid && !m_ready) begin
            a_f_elastic_002_ready_low: assert(!s_ready);
            a_f_elastic_002_no_input_fire: assert(!f_in_fire);
        end

        if (f_past_valid && !rst) begin
            a_f_elastic_003_occupancy_legal: assert(f_occupancy <= 2'd1);
            a_f_elastic_003_state_matches: assert(
                (f_occupancy == 2'd0 && !m_valid) ||
                (f_occupancy == 2'd1 && m_valid && m_data == f_token_data)
            );
        end

        c_stage_occupied: cover(f_past_valid && !rst && m_valid);
        c_output_stalled: cover(f_past_valid && !rst && m_valid && !m_ready);
        c_stall_then_transfer: cover(
            f_past_valid && !rst && !$past(rst) &&
            $past(m_valid && !m_ready) && m_valid && m_ready &&
            m_data == $past(m_data)
        );
        c_empty_stage_accept: cover(
            f_past_valid && !rst && !m_valid && s_valid && s_ready
        );
        c_simultaneous_pop_push: cover(
            f_past_valid && !rst && m_valid && m_ready && s_valid && s_ready
        );
    end

endmodule
