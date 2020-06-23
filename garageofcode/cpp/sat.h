#include <set>
#include <map>
#include <vector>

#define CLAUSES map<int, set<int>> // a mapping clause_id -> set of literals
#define VARS map<int, set<int>> // a mapping var_id -> set of clauses
#define CNF_CLAUSES set<int> // a set of clause_id
#define CNF_VARS set<int> // a set of var_id
#define ASSIGNMENT map<int, int> // a mapping var_id -> bool, may be partial
#define VECTOR vector<int>

using namespace std;

CLAUSES clauses;
VARS vars;

int sign(int a);

void print_map(VARS m);

bool assume(CNF_CLAUSES& cnf_clauses, CNF_VARS& cnf_vars, int lit);

bool solve(CNF_CLAUSES& cnf_clauses, CNF_VARS& cnf_vars, ASSIGNMENT assignment);

int main(int argc, char const *argv[]);


