#include <stdio.h>
#include <stdlib.h>
#include <iostream>
#include <fstream>
#include <vector>
using namespace std;

/*
*/
void write_to_file(std::vector<std::vector<int>> coords){
    ofstream f;
    f.open("data.txt");

    int i, j;
    char buffer [50];

    for(int k=0; k < coords.size(); k++){
        i = coords[k][0];
        j = coords[k][1];
        sprintf(buffer, "%d %d\n", i, j);
        //cout << buffer;
        f << buffer;
    }

    //f << "1 1\n 2 4\n 3 9\n 4 16";
    f.close();

}

/*
std::vector<std::vector<int>> copy_vector(std::vector<std::vector<int>> orig){
    std::vector<std::vector<int>> neu;
    for(int i=0; i < orig.size(); i++){
        std:vector<int> neurow;
        std::vector<int> row;
        row = orig[i];
        for(int j=0; j < row.size(); j++){
            neurow.push_back(row[j]);
        }
        neu.push_back(neurow);
    }
    return neu;
}
*/

std::vector<std::vector<int>> greedy_init(std::vector<std::vector<int>> coords){
    int i, nearest_idx, nearest_dist, dist;
    int x0, y0, x1, y1;
    std::vector<std::vector<int>> neu;
    std::vector<int> row;
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
        std::vector<int> row;    
        row.push_back(x0);
        row.push_back(y0);
        neu.push_back(row);
    }
    return neu;
}


int main ()
{
    const int N = 10000;
    std::vector<std::vector<int>> coords;
    std::vector<std::vector<int>> coords_neu;

    for(int k=0; k < N; k++){
        std::vector<int> row;
        row.push_back(rand() % 100);
        row.push_back(rand() % 100);
        coords.push_back(row);
    }

    //printf("%lu\n", coords.size());
    //coords_copy = copy_vector(coords);
    //printf("%p\n", &coords[0][0]);
    //printf("%p\n", &coords_copy[0][0]);
    coords_neu = greedy_init(coords);
    //printf("%lu\n", coords.size());
    printf("%lu\n", coords_neu.size());

    write_to_file(coords_neu);
}