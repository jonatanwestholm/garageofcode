#include <stdio.h>
#include <time.h>

int num_combs(int* vals, int target, int num_vals){
    if(target == 0){
        return 1;
    }
    if(target < 0){
        return 0;
    }
    if(num_vals == 0){
        return 0;
    }

    return num_combs(vals, target - vals[0], num_vals) +
           num_combs(vals + 1, target, num_vals - 1);
}

int main(){
    clock_t t0, t1;
    t0 = clock();

    int num_vals = 8;
    int vals[8] = {200, 100, 50, 20, 10, 5, 2, 1};
    int target = 200;

    printf("%d\n", num_combs(vals, target, num_vals));
    t1 = clock();
    printf("Time: %f\n", (double)(t1 - t0) / CLOCKS_PER_SEC);

    /*
    int* p;
    printf("%p\n", vals);
    p = vals;
    printf("%d\n", *p);
    p = vals + 1;
    printf("%p\n", p);
    printf("%d\n", *p);
    */
}