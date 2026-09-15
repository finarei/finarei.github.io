
/*
       Name : Josefine Reinhardsen
       Date : 05 / 12 / 2025
       File : Final.cpp
Description : Fills array a and b, 
              each in range [0, 50], 
              and ensures atleast one 
              element of arrays a and b, 
              in the same position in 
              both arrays, is the same
*/


#include <iostream>
#include <iomanip>
#include <ctime>

using namespace std;

const int ROW_SIZE = 4;
const int COL_SIZE = 4;
const int LOW = 0;
const int HIGH = 50;

unsigned int seed = (unsigned int)time(0);

void position(const int a[][COL_SIZE], const int b[][COL_SIZE]);
void print_array(const int a[][COL_SIZE]);
void cond_b(const int a[][COL_SIZE], int b[][COL_SIZE]);
void fill_array(int a[][COL_SIZE]);
int random_int(int low, int high);
double random(unsigned int& seed);

int main()
{
    int a[ROW_SIZE][COL_SIZE], b[ROW_SIZE][COL_SIZE];

    fill_array(a);
    cond_b(a, b);

    cout << endl;
    cout << "Array a:" << endl;
    print_array(a);
    cout << endl;
    cout << "Array b:" << endl;
    print_array(b);
    cout << endl;
    cout << "Position of the first equal elements:" << endl;
    position(a, b);

    return 0;
}

void position(const int a[][COL_SIZE], const int b[][COL_SIZE])
{
    for (int row = 0; row < ROW_SIZE; ++row)
        for (int col = 0; col < COL_SIZE; ++col)
            if (a[row][col] == b[row][col])
            {
                cout << "Row = " << row << endl 
                     << "Col = " << col << endl;
                return;
            }
}

void print_array(const int a[][COL_SIZE])
{
    for (int row = 0; row < ROW_SIZE; ++row)
    {
        for (int col = 0; col < COL_SIZE; ++col)
            cout << setw(4) << a[row][col];
        cout << endl;
    }
}

void cond_b(const int a[][COL_SIZE], int b[][COL_SIZE])
{
    bool diff = true;

    while (diff)
    {
        fill_array(b);
        for (int row = 0; row < ROW_SIZE; ++row)
            for (int col = 0; col < COL_SIZE; ++col)
                if (a[row][col] == b[row][col])
                   diff = false;
    }
}

void fill_array(int a[][COL_SIZE])
{
    for (int row = 0; row < ROW_SIZE; ++row)
        for (int col = 0; col < COL_SIZE; ++col)
            a[row][col] = random_int(LOW, HIGH);
}

int random_int(int low, int high)
{
    return int(low + (high - low + 1) * random(seed));
}

double random(unsigned int& seed)
{
    const int MODULUS = 15749;
    const int MULTIPLIER = 69069;
    const int INCREMENT = 1;

    seed = ((MULTIPLIER * seed) + INCREMENT) % MODULUS;

    return double(seed) / MODULUS;
}


/*
Sample run of the program:

Array a:
  47   6  16  22
  29  28  48  34
   6  41  49  46
  35  41   0  46

Array b:
  39  31  42  27
  32  19  48  31
  50  17  30  32
  24  33  43  48

Position of the first equal elements:
Row = 1
Col = 2

*/
