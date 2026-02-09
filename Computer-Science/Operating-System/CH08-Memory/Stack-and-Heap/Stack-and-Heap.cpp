#include <iostream>
using namespace std; // 이 줄을 추가하면!

int main() {
    int stackVar = 10;
    int* heapVar = new int(20);

    cout << "스택 주소: " << &stackVar << endl; // std:: 생략!
    cout << "힙 주소: " << heapVar << endl;

    delete heapVar;
    return 0;
}