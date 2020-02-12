#include <stdio.h>
#include <stdlib.h>

#define N 113384

int* memo; 

int collatz(int n){
    if(n < N){
        if(memo[n] > 0){
            return memo[n];
        }
    }
    int val;
    if(n % 2 == 0){
        val = 1 + collatz(n / 2);
        if(n < N){
            memo[n] = val;
        }
        return val;
    }else{
        val = 1 + collatz(3*n + 1);
        if(n < N){
            memo[n] = val;
        }
        return val;
    }
}

int main(){
    memo = (int*)calloc(N, sizeof(int));
    memo[0] = 1;
    memo[1] = 1;
    int longest, best_n, chain_length;
    longest = 0;
    best_n = 0;
    for(int n = 113384; n < N; n++){
        chain_length = collatz(n);
        if(chain_length > longest){
            best_n = n;
            longest = chain_length;
        }
    }
    printf("best_n: %d\n", best_n);
}