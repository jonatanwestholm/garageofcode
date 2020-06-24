#include <string>
#include <stdlib.h>

using namespace std;

int solution(int N){
    bool is_negative = N < 0;

    std::string s = std::to_string(N);
    int digit;
    int i = (int) is_negative;
    while (i < s.size()){
        digit = s[i] - '0';
        if(is_negative){
            if(digit > 5){
                break;
            }
        }else{
            if(digit < 5){
                break;
            }            
        }
        i++;
    }
    s.insert(i, "5");
    return std::stoi(s);
}

int main(){
    printf("%d\n", solution(0));
}