#include <stdio.h>
#include <math.h>

using namespace std;

int main(int argc, char const *argv[])
{
    int a = 1, b = 2, s = 2, c = 0;
    while(b < 4000000){
        c = a + b;
        a = b;
        b = c;
        if(b % 2 == 0){
            s += b;
        }
    }
    printf("%d\n", s);
}