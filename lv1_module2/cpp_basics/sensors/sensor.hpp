#pragma once

#include <string>

class Sensor {
public:
    explicit Sensor(std::string name);
    virtual ~Sensor();

    virtual double read() = 0;
    const std::string& name() const;

private:
    std::string name_;
};

class Lidar : public Sensor {
public:
    explicit Lidar(std::string name);
    ~Lidar() override;
    double read() override;
};

class Imu : public Sensor {
public:
    explicit Imu(std::string name);
    ~Imu() override;
    double read() override;
};

template <typename T>
T clamp(T value, T low, T high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}
