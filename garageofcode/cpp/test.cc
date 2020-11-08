#include <iostream>
#include <map>

#define MAP std::map<int, int>

void modify_map(MAP m){
    m[1] = 1;
}

int main(int argc, char const *argv[])
{
    MAP m;
    int a = m[1];
    printf("%d\n", a);
}