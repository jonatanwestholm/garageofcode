#include <stdio.h>
#include <math.h>
#include <vector>

using namespace std;

bool is_prime(vector<int> primes, int p){
    int i = 0;
    while(i < primes.size() && primes[i] < sqrt(p) + 1){
        if(p % primes[i] == 0){
            return false;
        }
        i += 1;
    }
    return true;
}

int main(int argc, char const *argv[])
{
    int p = 2;
    vector<int> primes;
    //primes.push_back(p)
    unsigned long n = 600851475143;
    while(n > 1){
        while(not is_prime(primes, p)){
            p += 1;
        }
        //printf("prime: %d\n", p);
        primes.push_back(p);

        while(n % p == 0){
            n = n / p;
        }
        p += 1;
    }

    printf("%d\n", primes[primes.size() - 1]);
}