#include <map>
#include <vector>
#include <math.h>

using namespace std;

int solution(vector<int> A){
    map<int, int> m;

    // Count the number of occurences of each integer
    for(int a : A){
        if(m.count(a)){
            m[a]++;
        }else{
            m[a] = 1;
        }
    }

    int sum = 0;
    for(const auto& [_, num_occurences] : m){
        sum += num_occurences * (num_occurences - 1) / 2;
    }

    return min(sum, 1000000000);
}

int main(){
    vector<int> A = {3, 5, 6, 5, 3, 3};
    printf("%d\n", solution(A));
}