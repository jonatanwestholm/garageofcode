#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string>

using namespace std;

bool is_palindrome(int N){
    std::string s = to_string(N);
    //cout << s.size();
    //cout << "\n";
    for(int i=0; i < s.size() / 2; i++){
        //printf("%d\n", i);
        if(s[i] != s[s.size() - 1 - i]){
            return false;
        }
    }
    return true;
}

int main(int argc, char const *argv[])
{
    /*
    printf("0: %d\n", is_palindrome(0.0));
    printf("10: %d\n", is_palindrome(10));
    printf("11: %d\n", is_palindrome(11));
    printf("101: %d\n", is_palindrome(101));
    printf("1011111: %d\n", is_palindrome(1011111));
    return 0; 
    */

    int j, val;
    int M = 1000;
    int highest_palindrome = 0;
    for(int d=2; d < 200; d++){
        for(int k=(d+1)/2; k > 0; k--){
            j = d - k;
            val = (M - k) * (M - j);
            if(is_palindrome(val)){
                printf("%d\n", val);
                printf("%d\n", M-k);
                printf("%d\n", M-j);
                if(val > highest_palindrome){
                    highest_palindrome = val;
                }
            }
        }
    }
    printf("best: %d\n", highest_palindrome);
}