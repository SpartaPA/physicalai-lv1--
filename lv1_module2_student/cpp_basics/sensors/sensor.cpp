#include "sensor.hpp"

#include <iostream>
#include <utility>

Sensor::Sensor(std::string name) : name_(std::move(name)) {
    std::cout << "Construct Sensor: " << name_ << '\n';
}

Sensor::~Sensor() {
    std::cout << "Destroy Sensor: " << name_ << '\n';
}

const std::string& Sensor::name() const {
    return name_;
}

Lidar::Lidar(std::string name) : Sensor(std::move(name)) {
    std::cout << "Construct Lidar\n";
}

Lidar::~Lidar() {
    std::cout << "Destroy Lidar\n";
}

double Lidar::read() {
    return 2.4;
}

Imu::Imu(std::string name) : Sensor(std::move(name)) {
    std::cout << "Construct Imu\n";
}

Imu::~Imu() {
    std::cout << "Destroy Imu\n";
}

double Imu::read() {
    return 0.15;
}
