#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <iostream>
#include <fstream>
#include <vector>
using namespace std;

#define IVEC std::vector<int>
#define VEC std::vector<double>
#define MAT std::vector<std::vector<double>>

/*
*/

MAT greedy_init(MAT coords){
    int i, nearest_idx, nearest_dist, dist;
    int x0, y0, x1, y1;
    MAT neu;
    VEC row;
    int k = rand() % coords.size();
    x0 = coords[k][0];
    y0 = coords[k][1];
    coords.erase(coords.begin() + k);
    row.push_back(x0);
    row.push_back(y0);
    neu.push_back(row);
    while(coords.size() > 0){
        //printf("Size: %lu\n", coords.size());
        nearest_dist = 999111999;
        nearest_idx = 0;
        for(i=0; i < coords.size(); i++){
            x1 = coords[i][0];
            y1 = coords[i][1];
            dist = (x0-x1)*(x0-x1) + (y0-y1)*(y0-y1);
            if(dist < nearest_dist){
                //printf("%d\n", dist);
                nearest_dist = dist;
                nearest_idx = i;
            }
        }
        //printf("%d\n", nearest_idx);

        x0 = coords[nearest_idx][0];
        y0 = coords[nearest_idx][1];
        coords.erase(coords.begin() + nearest_idx);
        VEC row;    
        row.push_back(x0);
        row.push_back(y0);
        neu.push_back(row);
    }
    return neu;
}

IVEC get_path(IVEC perm, int u){
    int u0 = u;
    IVEC path;
    path.push_back(u);
    u = perm[u];
    while(u != u0){
        u = perm[u];
        path.push_back(u);
    }
    return path;
}

double dist(VEC p0, VEC p1){
    return sqrt(pow(p0[0] - p1[0], 2.0) + pow(p0[1] - p1[1], 2.0));
}


bool improving_cross(VEC p0, VEC p1, VEC q0, VEC q1){ 
    return dist(p0, q0) + dist(p1, q1) < dist(p0, p1) + dist(q0, q1);
}

auto reverse_cycle(IVEC perm, int u){
    IVEC path = get_path(perm, u);
    int N = path.size();
    if(N > 1){
        for(int i=0; i < N; i++){
            perm[path[i]] = path[(i-1) % N];
        }        
        return perm, path[1];
    }else{
        return perm, path[0];
    }
}

IVEC cross_switch(IVEC perm, int u, int v){
    int tmp;
    tmp = perm[u];
    perm[u] = perm[v];
    perm[v] = tmp;

    perm, u = reverse_cycle(perm, u);
    
    tmp = perm[u];
    perm[u] = perm[v];
    perm[v] = tmp;
    
    return perm;
}

IVEC exhaust_crosses(MAT coords, IVEC perm){
    int N = perm.size();
    int tmp;
    VEC p0, p1, q0, q1;
    while(1){
        for(int i=0; i < N; i++){
            p0 = coords[i];
            p1 = coords[perm[i]];
            for(int j=i+1; j < N; j++){
                q0 = coords[j];
                q1 = coords[perm[j]];
                if(improving_cross(p0, p1, q0, q1)){
                    perm = cross_switch(perm, i, j);
                }
            }
        }
    }
}

void write_to_file(MAT coords, IVEC perm){
    ofstream f;
    f.open("data.txt");

    int i, j;
    char buffer [50];

    IVEC path = get_path(perm, 0);
    for(int k=0; k < path.size(); k++){
        i = coords[path[k]][0];
        j = coords[path[k]][1];
        sprintf(buffer, "%d %d\n", i, j);
        //cout << buffer;
        f << buffer;
    }

    //f << "1 1\n 2 4\n 3 9\n 4 16";
    f.close();

}

int main ()
{
    const int N = 30;
    MAT coords;
    IVEC perm;

    for(int k=0; k < N; k++){
        VEC row;
        //row.push_back(rand() % 100);
        //row.push_back(rand() % 100);
        row.push_back(10.0 * cos(k * 1.0 / N * 2 * M_PI));
        row.push_back(10.0 * sin(k * 1.0 / N * 2 * M_PI));
        coords.push_back(row);

        perm.push_back((k + 1) % N);
    }

    //printf("%lu\n", coords.size());
    //coords_copy = copy_vector(coords);
    //printf("%p\n", &coords[0][0]);
    //printf("%p\n", &coords_copy[0][0]);
    coords = greedy_init(coords);

    //printf("%lu\n", coords.size());
    IVEC path = get_path(perm, 0);
    printf("%lu\n", path.size());


    perm = cross_switch(perm, 0, 2);
    path = get_path(perm, 0);
    printf("%lu\n", path.size());
    printf("%d %d\n", perm[0], perm[2]);

    write_to_file(coords, perm);
    //perm = rnr_iter(coords, perm);
}