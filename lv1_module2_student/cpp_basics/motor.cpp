#include "motor.hpp"

#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <utility>

Motor::Motor(std::string name)
    : name_(std::move(name)), speed_(0.0) {}

void Motor::set_speed(double speed) {
    if (speed < 0.0) {
        throw std::invalid_argument("motor speed must be non-negative");
    }
    speed_ = speed;
}

void Motor::stop() {
    speed_ = 0.0;
}

void Motor::print_status() const {
    std::cout << std::fixed << std::setprecision(2)
              << name_ << " motor speed: " << speed_ << " m/s\n";
}

const std::string& Motor::name() const {
    return name_;
}

double Motor::speed() const {
    return speed_;
}
