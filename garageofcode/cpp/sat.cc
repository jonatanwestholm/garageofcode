#include <iostream>
#include <math.h>

#include "sat.h"

// lit is a var with a sign, denoting whether it's true or false

bool is_empty_clause(CNF_VARS* cnf_vars, int clause){
    for(const auto& lit: clauses[clause]){
        if(cnf_vars->count(abs(lit))){
            return false;
        }
    }
    return true;
}

bool assume(CNF_CLAUSES* cnf_clauses, CNF_VARS* cnf_vars, ASSIGNMENT* assignment, int lit){
    int clause; 
    int var = abs(lit);
    cnf_vars->erase(var);
    for(const auto& lit_clause: vars[var]){
        clause = abs(lit_clause);
        if(not cnf_clauses->count(clause)){
            continue;
        }
        if(lit * lit_clause > 0){
            cnf_clauses->erase(clause);
            printf("size of cnf_clauses: %lu\n", cnf_clauses->size());
        }else{
            if(is_empty_clause(cnf_vars, clause)){
                return false;
            }    
        }
    }
    (*assignment)[var] = lit;
    return true;
}

void unassume(CNF_CLAUSES* cnf_clauses, CNF_VARS* cnf_vars, ASSIGNMENT* assignment, int lit){
    int clause;
    bool still_satisfied;
    int var = abs(lit);
    cnf_vars->insert(var); // the var always goes back to the active vars
    assignment->erase(var); // the assignment always gets erased
    for(const auto& lit_clause: vars[var]){
        clause = abs(lit_clause);
        still_satisfied = false;
        for(const auto& sister_lit: clauses[clause]){
            // loop to see if clause is still satisfied with current assignment
            if(assignment->count(abs(sister_lit)) and (*assignment)[abs(sister_lit)] * sister_lit > 0){
                still_satisfied = true;
                break;
            }
        }
        if(not still_satisfied){
            // then we have to add the clause back to the active clauses
            cnf_clauses->insert(clause);
        }
    }
}

int get_priority(CNF_CLAUSES* cnf_clauses, CNF_VARS* cnf_vars){
    /*
    int least_decreased = cnf_clauses.size();
    int best_lit;
    int pos_count, neg_count;
    for(const auto& var: cnf_vars){
        pos_count = 0;
        neg_count = 0;
        for(const auto& lit_clause: vars[var]){
            if(cnf_clauses.count(abs(lit_clause))){
                if(lit_clause < 0){
                    neg_count++;
                }else{
                    pos_count++;
                }
            }
        }
        num_decreased = min(pos_count, neg_count);
        if(num_decreased < least_decreased){
            least_decreased = num_decreased;
            if(pos_count > neg_count){
                best_lit = var;
            }else{
                best_lit = -var;
            }
        }
    }
    VECTOR prio;
    prio.push_back(best_lit);
    prio.push_back(-best_lit);
    */

    // to begin with: just return the first var
    for(const auto& var: (*cnf_vars)){
        return var;
    }
}


bool solve(CNF_CLAUSES* cnf_clauses, CNF_VARS* cnf_vars, ASSIGNMENT* assignment){
    if(not cnf_clauses->size()){
        return true;
    }

    int best_lit, lit, var;

    best_lit = get_priority(cnf_clauses, cnf_vars);
    printf("best_lit: %d\n", best_lit);
    for(const auto& lit: {best_lit, -best_lit}){
        printf("lit: %d\n", lit);
        var = abs(lit);
        // either assumption fails right away b.c. clause gets empty
        // or it fails down the line
        if(assume(cnf_clauses, cnf_vars, assignment, lit)){
            printf("size cnf_clauses, post assume: %lu\n", cnf_clauses->size());
            if(solve(cnf_clauses, cnf_vars, assignment)){
                // assumption worked - walk up
                return true;
            }else{
                // assumption didn't work, continue
            }
        }
        unassume(cnf_clauses, cnf_vars, assignment, lit);
    }
    // if assuming a lit and its negation both lead to unsatisfiable cases,
    // then the cnf is not satisfiable
    return false;
}


int main(int argc, char const *argv[])
{
    CNF_CLAUSES cnf_clauses;
    CNF_VARS cnf_vars;
    ASSIGNMENT assignment;
    bool solved;

    //clauses[1] = {1, 2};
    //clauses[2] = {-1, -2};
    clauses[1] = {1, 2, 3};
    clauses[2] = {1, -2, -3};
    clauses[3] = {-1, 2, -3};
    clauses[4] = {-1, -2, 3};
    clauses[5] = {-1, -2, -3};
    clauses[6] = {3};

    int var;
    int sgn;
    for(const auto& [clause, literals]: clauses){
        for(const auto& lit: literals){
            var = abs(lit);
            sgn = sign(lit);
            if(vars.count(var)){
                vars[var].insert(sgn * clause);
            }else{
                vars[var] = {sgn * clause};
            }

            cnf_vars.insert(var);
        }
        cnf_clauses.insert(clause);
    }

    solved = solve(&cnf_clauses, &cnf_vars, &assignment);
    printf("solved: %s\n", solved? "TRUE": "FALSE");
    for(const auto& [var, lit]: assignment){
        cout << lit << " ";
    }
    cout << "\n";

}


int sign(int a){
    if(a > 0){
        return 1;
    }else{
        return -1;
    }
}


void print_map(VARS m){
    for(const auto& [key, value]: m){
        cout << key << ":";
        for(const auto& i: value){
            cout << " " << i;
        }
        cout << "\n";
    }
}


/* Recursion-free version
ASSIGNMENT solve(CNF_CLAUSES cnf_clauses, CNF_VARS cnf_vars){
    int lit;
    int var;
    ASSIGNMENT assignment;
    VECTOR stack;

    while(cnf_clauses.size()){
        lit = get_priority(cnf_clauses, cnf_vars);
        var = abs(lit);
        if(assume(cnf_clauses, cnf_vars, lit)){
            assignment[var] = sign(lit);
            stack.push_back(var);
        }else{
            unassume(cnf_clauses, cnf_vars, abs(lit));
            assignment.erase(abs(lit));
        }
    }

}
*/
