module out(

);

wire [`DataWidth] test_a_c;


test_a test_a0(
.a_a(),
.a_b(),
.a_c(test_a_c)
);

test_b test_b0(
.b_clk(),
.b_d(test_a_c),
.b_e()
);

