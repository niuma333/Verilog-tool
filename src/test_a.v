module test_a(
input [`DataWidth] a,
input [`DataWidth]b,
output [`DataWidth]c
);
assign c=a&&b;
endmodule