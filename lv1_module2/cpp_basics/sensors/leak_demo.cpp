#include <iostream>
#include <memory>
#include <string>

int main(int argc, char* argv[]) {
    const std::string mode = argc > 1 ? argv[1] : "leak";

    if (mode == "leak") {
        for (int i = 0; i < 3; ++i) {
            auto* samples = new double[1024];
            samples[0] = i;
        }
        std::cout << "Finished leak mode\n";
        return 0;
    }

    if (mode == "fixed") {
        for (int i = 0; i < 3; ++i) {
            auto samples = std::make_unique<double[]>(1024);
            samples[0] = i;
        }
        std::cout << "Finished fixed mode\n";
        return 0;
    }

    std::cerr << "Usage: leak_demo [leak|fixed]\n";
    return 1;
}
