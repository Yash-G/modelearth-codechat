#include <iostream>

int main() {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}

class MyClass {
    int value = 42;
public:
    std::string greet() {
        return "Hello from C++!";
    }
};
