#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

class Rational{
  public:
    int p; 
    int q;

    Rational(std::pair<int, int> pq){
      //check that q != 0
      p = pq.first;
      q = pq.second;

      this->reduce();
    }

    Rational(int p0){
      //check that q != 0
      p = p0;
      q = 1;
    }

    Rational operator*(Rational other){
      return Rational({this->p * other.p, this->q * other.q});
    }
  
    Rational operator/(Rational other){
      //check that other.p != 0
      return Rational({this->p * other.q, this->q * other.p});
    }

    Rational operator+(Rational other){
      return Rational({this->p * other.q + this->q * other.p, this->q * other.q});
    }

    Rational operator-(Rational other){
      return Rational({this->p * other.q - this->q * other.p, this->q * other.q});
    }    

    void reduce(){
      int a, b, tmp;
      if(this->p > this->q){
        a = this->q;
        b = this->p;
      }else{
        a = this->p;
        b = this->q;        
      }
      // a <= b
      while(a > 0){
        tmp = a;
        a = b % a;
        b = tmp;
      }
      // b is gcd
      this->p /= b;
      this->q /= b;
    }

    friend ostream& operator<<(ostream& os, const Rational& r);
};

ostream& operator<<(ostream& os, const Rational& r){
  os << r.p << "/" << r.q;
  return os;
}  

void reduce_row(vector<Rational>& row0, vector<Rational>& row1, int col){
  // subtracts a multiple of row0 from row1 such that the element 
  // on index col is 0
  // changes row1
  // check that col < len(row0) == len(row1)
  // check that row0[col] != 0
  auto c = row1[col] / row0[col];
  for(int j = 0; j < row0.size(); ++j){
    auto r0 = row0[j];
    auto r1 = row1[j];
    row1[j] = r1 - r0 * c;
  }
}

int find_unpopped_nonzero(vector<vector<Rational>>& A, int i, int j){
  int n = A.size();
  while(true){
    if(i >= n){
      return -1;
    }
    if(A[i][j].p != 0){
      return i;
    }
    ++i;
  }
}

void gaussian_elimination(vector<vector<Rational>>& A){
  /*
  while there are more rows or columns to reduce
  find an unpopped nonzero element in the first unpopped column
    move this row to the top unpopped row
  if none such can be found, go to the next column (continue)
  when such an element is found, reduce all rows below and continue
  */
  int n = A.size();
  if(n == 0){return;}
  int m = A[0].size();
  int i = 0;
  int j = 0;
  int i_f; // f is for fresh
  while(i < n && j < m){
    i_f = find_unpopped_nonzero(A, i, j);
    if(i_f == -1){
      ++j;
      continue;
    }else{
      iter_swap(A.begin() + i, A.begin() + i_f);
    }

    for(int i1 = i+1; i1 < n; ++i1){
      reduce_row(A[i], A[i1], j);
    }
    ++i;
    ++j;
  }
  return;
}

int main() {
  /*
  auto r = Rational({2, 3});
  auto s = Rational({2, 4});
  auto x = r - s;

  vector<Rational> row0 = {1, 2, 3};
  vector<Rational> row1 = {4, 5, 6};
  vector<Rational> row2 = {7, 8, 9};
  */
  
  vector<vector<Rational>> A;
  A.push_back(vector<Rational>{1, 2, 3});
  A.push_back(vector<Rational>{4, 5, 6});
  A.push_back(vector<Rational>{7, 8, 9});

  gaussian_elimination(A);

  for(const auto row : A){
    for(const auto r : row){
      cout << r << ", ";
    }
    cout << "\n";
  }

  /*
  reduce_row(row0, row2, 0);

  for(auto r : row2){
    cout << r << ", ";
  }

  cout << "\n";
  */

  return 0;
}