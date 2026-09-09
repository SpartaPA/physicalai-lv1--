#include <iostream>
#include <memory>

class SensorWithoutVirtualDestructor {
public:
    ~SensorWithoutVirtualDestructor() {
        std::cout << "Destroy base sensor\n";
    }

    virtual double read() = 0;
};

class LidarWithoutVirtualDestructor : public SensorWithoutVirtualDestructor {
public:
    ~LidarWithoutVirtualDestructor() {
        std::cout << "Destroy derived lidar\n";
    }

    double read() override {
        return 1.0;
    }

private:
    double scan_[128]{};
};

int main() {
    std::unique_ptr<SensorWithoutVirtualDestructor> sensor =
        std::make_unique<LidarWithoutVirtualDestructor>();
    std::cout << "Read: " << sensor->read() << '\n';
    return 0;
}
