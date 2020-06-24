#include <set>
#include <vector>
#include <algorithm>

using namespace std;

int solution(vector<int> X){
    set<int> s;
    vector<int> v;

    // Make a set
    for (int x : X){
        s.insert(x);
    }

    // Turn it into a vector
    for (const auto& key : s){
        v.push_back(key);
    }

    sort(v.begin(), v.end());

    int max_diff = 0;
    int diff;
    for(int i=0; i < v.size() - 1; i++){
        diff = v[i+1] - v[i];
        if(diff > max_diff){
            max_diff = diff;
        }
    }

    return max_diff;
}

int main(){
    vector<int> X = {-10, 1, 1, 2, 3};
    printf("%d\n", solution(X)); 

}