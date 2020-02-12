int get_primes(int n, int* primes){
    int i, j;
    int memo_length = 100;
    int memo[memo_length];
    int num_primes = 0;

    i = 2;
    while(i <= n){
        for(j = 0; j < num_primes; j++){
            if(i % memo[j] == 0){
                break
            }
        }
        if(j == num_primes){
            memo[num_primes] = i;
            num_primes += 1;

            /*
            if(num_primes >= memo_length){
                memo_length *= 2;
                memo = realloc(memo, memo_length * sizeof(int));
            }
            */
        }
        i += 1;
    }
    return num_primes
}