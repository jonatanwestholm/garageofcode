#include <stdio.h>
#include <math.h>

using namespace std;

int main(int argc, char const *argv[])
{
    int s = 0;
    for(int i=0; i < 1000; i++){
        if(i % 3 == 0 or i % 5 == 0){
            s += i;
        }
    }
    printf("%d\n", s);
}