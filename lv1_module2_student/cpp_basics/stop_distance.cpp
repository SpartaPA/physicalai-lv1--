#include <iomanip>
#include <iostream>

namespace {
constexpr double kGravity = 9.81;

double calculate_stop_distance(double speed, double friction_coefficient) {
    return speed * speed / (2.0 * friction_coefficient * kGravity);
}
}

int main() {
    double speed = 0.0;
    double friction_coefficient = 0.0;

    std::cout << "Enter speed (m/s): ";
    if (!(std::cin >> speed)) {
        std::cerr << "Error: speed type number.\n";
        return 1;
    }

    std::cout << "Enter friction coefficient: ";
    if (!(std::cin >> friction_coefficient)) {
        std::cerr << "Error: friction coefficient type number.\n";
        return 1;
    }

    if (speed < 0.0) {
        std::cerr << "Error: speed type non-negative.\n";
        return 1;
    }

    if (friction_coefficient <= 0.0) {
        std::cerr << "Error: friction coefficient type greater than zero.\n";
        return 1;
    }

    const double stop_distance =
        calculate_stop_distance(speed, friction_coefficient);

    std::cout << std::fixed << std::setprecision(3)
              << "Stopping distance: " << stop_distance << " m\n";

    return 0;
}
