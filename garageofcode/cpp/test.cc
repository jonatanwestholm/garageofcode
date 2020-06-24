#include <iostream>
#include <map>

#define MAP std::map<int, int>

void modify_map(MAP m){
    m[1] = 1;
}

int main(int argc, char const *argv[])
{
    MAP m;
    m[1] = 0;
    modify_map(m);

    printf("%d\n", m[1]);

}