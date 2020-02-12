#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int get_factor(long n){
    for(int i = 2; i < n; i++){
        if(n % i == 0){
            return i;
        }
    }
}

int main(int argc, char* argv[]){
    clock_t t0, t1;
    t0 = clock();

    //long n = strtol(argv[1], NULL, 10);
    //printf("%ld\n", n);
    long n = 600851475143;
    //int n = 55;
    int p;
    while(1){
        p = get_factor(n);
        if(p == n) break;
        n = n / p;
    }
    
    t1 = clock();
    printf("p: %d\n", p);
    printf("Time: %f\n", (double)(t1 - t0) / CLOCKS_PER_SEC);
}