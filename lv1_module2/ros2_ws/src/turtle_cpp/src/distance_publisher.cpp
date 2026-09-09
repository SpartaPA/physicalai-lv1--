#include <chrono>
#include <cmath>
#include <memory>
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/float32.hpp"
#include "turtlesim/msg/pose.hpp"
using namespace std::chrono_literals;

class DistancePublisher : public rclcpp::Node
{
public:
  DistancePublisher()
  : Node("cpp_distance_publisher")
  {
    subscription_ = create_subscription<turtlesim::msg::Pose>(
      "/turtle1/pose", 10, [this](turtlesim::msg::Pose::SharedPtr msg) {
        x_ = msg->x; y_ = msg->y; received_ = true;
      });
    publisher_ = create_publisher<std_msgs::msg::Float32>("/turtle_distance", 10);
    timer_ = create_wall_timer(
      100ms, [this]() {
        if (!received_) {return;}
        std_msgs::msg::Float32 msg;
        msg.data = static_cast<float>(std::hypot(x_, y_));
        publisher_->publish(msg);
      });
  }

private:
  float x_{0.0F}, y_{0.0F};
  bool received_{false};
  rclcpp::Subscription<turtlesim::msg::Pose>::SharedPtr subscription_;
  rclcpp::Publisher<std_msgs::msg::Float32>::SharedPtr publisher_;
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<DistancePublisher>());
  rclcpp::shutdown();
  return 0;
}
