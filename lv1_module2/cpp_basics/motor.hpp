#pragma once

#include <string>

class Motor {
public:
    explicit Motor(std::string name);

    void set_speed(double speed);
    void stop();
    void print_status() const;

    const std::string& name() const;
    double speed() const;

private:
    std::string name_;
    double speed_;
};
