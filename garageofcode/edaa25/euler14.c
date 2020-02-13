#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define N 1000000

int* memo; 

int collatz(long n){
    //printf("%d\n", n);
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
    clock_t t0, t1;
    t0 = clock();
    memo = (int*)calloc(N, sizeof(int));
    memo[0] = 1;
    memo[1] = 1;
    int longest, best_n, chain_length;
    longest = 0;
    best_n = 0;
    for(long n = 2; n < N; n++){
        chain_length = collatz(n);
        if(chain_length > longest){
            best_n = n;
            longest = chain_length;
        }
    }
    t1 = clock();
    printf("%f\n", (double)(t1 - t0) / CLOCKS_PER_SEC);
    printf("best_n: %d longest: %d\n", best_n, longest);
}