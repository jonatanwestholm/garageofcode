int: N; % the number of employees
int: T; % the number of days
int: max_workdays;
array[1..T] of int: demand;

% variables
array[1..N, 1..T] of var bool: work;

constraint forall(i in 1..N)(sum(j in 1..T)(work[i, j]) <= max_workdays);
constraint forall(j in 1..T)(sum(i in 1..N)(work[i, j]) >= demand[j]);

% 
% data
% 

N = 3;
T = 3;
max_workdays = 2;
demand = [2, 2, 2];