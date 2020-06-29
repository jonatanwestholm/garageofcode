#include <cstdlib>
#include <iostream>
#include <fstream>
#include <cmath>
#include <string>
#include <chrono>

#include "sat.h"

// lit is a var with a sign, denoting whether it's true or false

//#define DEBUG printf
#define DEBUG //
int CALLS_TO_SOLVE = 0;

int nof_clauses(){
    return clauses.size();
}

int nof_vars(){
    return vars.size();
}

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
            DEBUG("size of cnf_clauses: %lu\n", cnf_clauses->size());
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

/*
int get_priority(CNF_CLAUSES* cnf_clauses, CNF_VARS* cnf_vars){
    for(const auto& var: (*cnf_vars)){
        return var;
    }
}

int get_priority(CNF_CLAUSES* cnf_clauses, CNF_VARS* cnf_vars){
    // pick most decreasing first
    // this tactic sucks
    int num_decreased;
    int most_decreased = 0;
    int best_lit;
    int pos_decreased, neg_decreased;
    for(const auto& var: *cnf_vars){
        pos_decreased = 0;
        neg_decreased = 0;
        for(const auto& lit_clause: vars[var]){
            if(cnf_clauses->count(abs(lit_clause))){
                if(lit_clause > 0){
                    neg_decreased++;
                }else{
                    pos_decreased++;
                }
            }
        }
        num_decreased = max(pos_decreased, neg_decreased);
        if(num_decreased > most_decreased){
            most_decreased = num_decreased;
            if(pos_decreased > neg_decreased){
                best_lit = var;
            }else{
                best_lit = -var;
            }
        }
    }
    return best_lit;
}
*/

/*
*/
int get_priority(CNF_CLAUSES* cnf_clauses, CNF_VARS* cnf_vars){
    // pick most satisfying first
    int num_satisfied;
    int most_satisfied = 0;
    int best_lit;
    int pos_satisfying, neg_satisfying;
    for(const auto& var: *cnf_vars){
        pos_satisfying = 0;
        neg_satisfying = 0;
        for(const auto& lit_clause: vars[var]){
            if(cnf_clauses->count(abs(lit_clause))){
                if(lit_clause < 0){
                    neg_satisfying++;
                }else{
                    pos_satisfying++;
                }
            }
        }
        num_satisfied = max(pos_satisfying, neg_satisfying);
        if(num_satisfied > most_satisfied){
            most_satisfied = num_satisfied;
            if(pos_satisfying > neg_satisfying){
                best_lit = var;
            }else{
                best_lit = -var;
            }
        }
    }
    return best_lit;
}

int get_trivial(CNF_CLAUSES* cnf_clauses, CNF_VARS* cnf_vars){
    int num_unassigned, lit;
    for(const auto& var: *cnf_vars){
        for(const auto& lit_clause: vars[var]){
            num_unassigned = 0;
            for(const auto& sister_lit: clauses[abs(lit_clause)]){
                if(cnf_vars->count(abs(sister_lit))){
                    num_unassigned++;
                    lit = sister_lit;
                }
            }
            if(num_unassigned == 1){
                // we found a clause with a single unassigned variable
                // - the lit must be assumed
                return lit;
            }
        }
    }
    return 0;
}


bool solve(CNF_CLAUSES* cnf_clauses, CNF_VARS* cnf_vars, ASSIGNMENT* assignment){
    CALLS_TO_SOLVE++;
    if(CALLS_TO_SOLVE % 10000 == 0){
        printf("calls to solve: %d\n", CALLS_TO_SOLVE);
    }
    if(not cnf_clauses->size()){
        return true;
    }

    int best_lit, lit, var;

    best_lit = get_trivial(cnf_clauses, cnf_vars); // check for trivial assignments
    if(not best_lit){
        best_lit = get_priority(cnf_clauses, cnf_vars);
    }
    DEBUG("best_lit: %d\n", best_lit);
    for(const auto& lit: {best_lit, -best_lit}){
        DEBUG("lit: %d\n", lit);
        var = abs(lit);
        // either assumption fails right away b.c. clause gets empty
        // or it fails down the line
        if(assume(cnf_clauses, cnf_vars, assignment, lit)){
            DEBUG("size cnf_clauses, post assume: %lu\n", cnf_clauses->size());
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

vector<std::string> split(std::string s, char delimiter){
    vector<std::string> v;
    int i;

    while(1){
        i = s.find(delimiter);
        if(i < 0){
            break;
        }
        v.push_back(s.substr(0, i));
        s = s.substr(i+1, s.length());
    }
    v.push_back(s);
    return v;
}


void read_from_file(){
    ifstream f;
    f.open("/home/jdw/garageofcode/results/sat/out.cnf");

    std::string line;
    std::getline(f, line); // skip the header

    int i = 1;
    while(std::getline(f, line)){
        set<int> s;
        vector<std::string> v = split(line, ' ');
        for(int j=0; j < v.size()-1; j++){
            s.insert(std::stoi(v[j]));
        }
        clauses[i] = s;
        i++;
    }

    f.close();
}

int main(int argc, char const *argv[])
{
    CNF_CLAUSES cnf_clauses;
    CNF_VARS cnf_vars;
    ASSIGNMENT assignment;
    bool solved;

    read_from_file();
    //print_map(clauses);
    //exit(0);

    //clauses[1] = {1, 2};
    //clauses[2] = {-1, -2};
    /*
    clauses[1] = {1, 2, 3};
    clauses[2] = {1, -2, -3};
    clauses[3] = {-1, 2, -3};
    clauses[4] = {-1, -2, 3};
    clauses[5] = {-1, -2, -3};
    clauses[6] = {3};
    */

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

    auto t0 = std::chrono::high_resolution_clock::now();
    solved = solve(&cnf_clauses, &cnf_vars, &assignment);
    auto t1 = std::chrono::high_resolution_clock::now();
    int total_time = (t1 - t0) / std::chrono::milliseconds(1);

    printf("solved: %s\n", solved? "TRUE": "FALSE");
    for(const auto& [var, lit]: assignment){
        cout << lit << " ";
    }
    cout << "\n";
    printf("Total calls to solve: %d\n", CALLS_TO_SOLVE);
    printf("Total time: %d ms\n", total_time);

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
