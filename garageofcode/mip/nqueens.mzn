int: n; % The number of queens.

array [1..n] of var 1..n: q;

include "alldifferent.mzn";

constraint alldifferent(q);
constraint alldifferent(i in 1..n)(q[i] + i);
constraint alldifferent(i in 1..n)(q[i] - i);

solve
    :: warm_start_array( [
        warm_start(q, [20, 15, 10, 16, 13, 21, 2, 17, 30, 9, 11, 29, 31, 28, 25, 8, 19, 12, 24, 6, 32, 23, 14, 27, 7, 22, 4, 18, 26, 5, 3, 1] ) ])
    satisfy;

n = 4;