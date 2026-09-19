module apb_regs (
    input  logic        clk,
    input  logic        rst,

    input  logic        psel,
    input  logic        penable,
    input  logic        pwrite,
    input  logic [7:0]  paddr,
    input  logic [31:0] pwdata,
    output logic [31:0] prdata,
    output logic        pready,
    output logic        pslverr,

    input  logic        processing_i,
    input  logic        draining_i,
    input  logic        sof_accept_i,
    input  logic        frame_error_set_i,
    input  logic        frame_done_i,

    output logic        run_enable_o,
    output logic [7:0]  threshold_active_o,
    output logic        bypass_threshold_active_o
);

    localparam logic [7:0] ADDR_CONTROL     = 8'h00;
    localparam logic [7:0] ADDR_THRESHOLD   = 8'h04;
    localparam logic [7:0] ADDR_STATUS      = 8'h08;
    localparam logic [7:0] ADDR_FRAME_COUNT = 8'h0C;

    logic [7:0]  threshold_shadow_q;
    logic        bypass_threshold_shadow_q;
    logic        frame_error_q;
    logic [31:0] frame_count_q;

    logic addr_valid;
    logic write_access;
    logic config_pending;
    logic status_w1c_error;

    always_comb begin
        case (paddr)
            ADDR_CONTROL,
            ADDR_THRESHOLD,
            ADDR_STATUS,
            ADDR_FRAME_COUNT: addr_valid = 1'b1;
            default:          addr_valid = 1'b0;
        endcase
    end

    assign pready       = 1'b1;
    assign pslverr      = psel && penable && !addr_valid;
    assign write_access = psel && penable && pwrite && addr_valid;

    assign config_pending =
        (threshold_shadow_q != threshold_active_o) ||
        (bypass_threshold_shadow_q != bypass_threshold_active_o);

    assign status_w1c_error =
        write_access &&
        (paddr == ADDR_STATUS) &&
        ((pwdata & 32'h0000_0008) != 32'd0);

    always_comb begin
        prdata = 32'd0;

        case (paddr)
            ADDR_CONTROL: begin
                prdata[0] = run_enable_o;
                prdata[1] = bypass_threshold_shadow_q;
            end

            ADDR_THRESHOLD: begin
                prdata[7:0] = threshold_shadow_q;
            end

            ADDR_STATUS: begin
                prdata[0] = processing_i || draining_i;
                prdata[1] = draining_i;
                prdata[2] = config_pending;
                prdata[3] = frame_error_q;
            end

            ADDR_FRAME_COUNT: begin
                prdata = frame_count_q;
            end

            default: begin
                prdata = 32'd0;
            end
        endcase
    end

    always_ff @(posedge clk) begin
        if (rst) begin
            run_enable_o                  <= 1'b0;
            threshold_shadow_q            <= 8'd128;
            threshold_active_o            <= 8'd128;
            bypass_threshold_shadow_q     <= 1'b0;
            bypass_threshold_active_o     <= 1'b0;
            frame_error_q                 <= 1'b0;
            frame_count_q                 <= 32'd0;
        end else begin
            if (write_access && (paddr == ADDR_CONTROL)) begin
                run_enable_o              <= pwdata[0];
                bypass_threshold_shadow_q <= pwdata[1];
            end

            if (write_access && (paddr == ADDR_THRESHOLD)) begin
                threshold_shadow_q <= pwdata[7:0];
            end

            if (sof_accept_i) begin
                threshold_active_o        <= threshold_shadow_q;
                bypass_threshold_active_o <= bypass_threshold_shadow_q;
            end

            if (frame_error_set_i) begin
                frame_error_q <= 1'b1;
            end else if (status_w1c_error) begin
                frame_error_q <= 1'b0;
            end

            if (frame_done_i) begin
                frame_count_q <= frame_count_q + 32'd1;
            end
        end
    end

endmodule
