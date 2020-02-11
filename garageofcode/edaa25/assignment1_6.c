#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define len(x) sizeof(x) / sizeof(x[0])

// gotta write a function to strip leading 0

int min(int a, int b){
    if(a <= b){
        return a;
    }else{
        return b;
    }
}

int max(int a, int b){
    if(a >= b){
        return a;
    }else{
        return b;
    }
}

int* convolve(int* c, int* a, int* b){
    int s;
    int e0;
    int e1;
    int k = len(c);

    for(int m = 0; m < k; m++){
        printf("%d\n", m);
        s = 0;
        e0 = max(0, m - len(b) + 1);
        e1 = min(m, len(a));

        for(int i = min(e0, e1); i < max(e0, e1); i++){
            printf("\t%d\n", i);
            s += a[i] * b[m - i];
        }
        c[m] = s;
    }
}

int* multiply(int* c, int* a, int* b){
    int k;
    int r;
    int x;
    k = len(c);
    convolve(c, a, b);

    /*
    for(int i = 0; i < k - 1; i++){
        x = c[i] / 10;
        r = c[i] % 10;
        c[i] = r;
        c[i + 1] += x;
    }
    */

    //return c[k - 1] == 0;
}


void main(){
    /*
    int n = 15;
    unsigned long n_factorial = 1;
    for(int i = 1; i <= n; i++){
        n_factorial = n_factorial * i;
    }
    printf("%ld\n", n_factorial);
    */
    //printf("%zu\n", );
    int a[1] = {1};
    int b[1] = {2};
    int k = len(a) + len(b);
    int c[k];

    multiply(c, a, b);

    for(int i = 0; i < k; i++){
        printf("%d,", c[i]);
    }
    printf("\n");
}