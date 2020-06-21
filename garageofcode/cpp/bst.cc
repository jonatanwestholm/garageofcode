#include <map>
#include <vector>
#include <math.h>
using namespace std;

class BSTNode
{
public:
    int weight;
    BSTNode *left = nullptr;
    BSTNode *right = nullptr;
    BSTNode(int weight){
        this->weight = weight;

    }
};

int max_path(BSTNode *node){
    if(node == nullptr){
        return 0;
    }

    return max(max_path(node->left), max_path(node->right)) + node->weight;
}

BSTNode* bst_from_vector(vector<int> v){
    if(v.size() == 0){
        return nullptr;
    }else if(v.size() == 1){
        BSTNode *node = new BSTNode(1);
        return node;
    }

    size_t mid = (v.end() - v.begin()) / 2;

    


}

int main(int argc, char const *argv[])
{
    BSTNode node = BSTNode(5);
    printf("%d\n", node.weight);
}