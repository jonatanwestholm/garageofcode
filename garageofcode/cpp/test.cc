#include <iostream>
#include <map>
#include <vector>

#define MAP std::map<int, int>

using namespace std;

void modify_map(MAP m){
    m[1] = 1;
}

int main(int argc, char const *argv[])
{
    /*
    MAP m;
    int a = m[1];
    printf("%d\n", a);

    std::optional<int> b;
    if(b){
      printf("yes b\n");
    }else{
      printf("no b\n");
    }
    */

    vector<double> a (10, 3);
    vector<double> b = a;
    b[0] = 1;
    cout << "a:" << a[0] << " " << a[9] << "\n";
    cout << "b:" << b[0] << " " << b[9] << "\n";
    a = b;
    cout << "a:" << a[0] << " " << a[9] << "\n";


}