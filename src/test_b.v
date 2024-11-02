module test_b(
input clk,
input [`DataWidth]d,
output [`DataWidth]e
);
always @(posedge clk) begin
e<=d;
end