#include "llfio.h"
#include <vector>
#include <string>

int main() {
    llfio();

    std::vector<std::string> vec;
    vec.push_back("test_package");

    llfio_print_vector(vec);
}
