#include "sensor.hpp"

#include <algorithm>
#include <iostream>
#include <memory>
#include <string>
#include <unordered_map>
#include <vector>

struct Measurement {
    std::string sensor_name;
    double value;
    double distance_to_goal;
};

int main() {
    std::cout << "[Stack lifetime]\n";
    {
        Lidar stack_lidar("stack_lidar");
        std::cout << stack_lidar.name() << " read: " << stack_lidar.read() << '\n';
    }
    std::cout << "Stack scope ended\n\n";

    std::cout << "[Polymorphic heap sensors]\n";
    std::vector<std::unique_ptr<Sensor>> sensors;
    sensors.push_back(std::make_unique<Lidar>("front_lidar"));
    sensors.push_back(std::make_unique<Imu>("body_imu"));

    std::unordered_map<std::string, double> latest_measurements;
    for (const auto& sensor : sensors) {
        const double value = sensor->read();
        latest_measurements[sensor->name()] = value;
        std::cout << sensor->name() << " read: " << value << '\n';
    }

    std::vector<Measurement> logs{
        {"front_lidar", 2.4, 0.20},
        {"body_imu", 0.15, 0.35},
        {"front_lidar", 1.8, 0.36},
        {"body_imu", 0.12, 0.10},
    };

    const auto near_count = std::count_if(
        logs.begin(), logs.end(),
        [](const Measurement& measurement) {
            return measurement.distance_to_goal <= 0.35;
        });

    std::cout << "Latest front_lidar: " << latest_measurements.at("front_lidar") << '\n';
    std::cout << "Records within 0.35: " << near_count << '\n';
    std::cout << "Clamped speed: " << clamp(3.2, 0.0, 2.0) << '\n';
    std::cout << "Clamped pixel: " << clamp(300, 0, 255) << '\n';
    std::cout << "Leaving main\n";

    return 0;
}
