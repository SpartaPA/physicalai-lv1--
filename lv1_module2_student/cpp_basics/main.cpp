#include "motor.hpp"

#include <iostream>

int main() {
    Motor left_motor("left");
    Motor right_motor("right");

    left_motor.set_speed(1.5);
    right_motor.set_speed(1.5);

    left_motor.print_status();
    right_motor.print_status();

    left_motor.stop();
    right_motor.stop();

    std::cout << "Motors stopped.\n";
    left_motor.print_status();
    right_motor.print_status();

    return 0;
}
