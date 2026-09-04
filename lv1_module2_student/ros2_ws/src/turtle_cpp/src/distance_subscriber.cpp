#include <memory>
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/float32.hpp"

class DistanceSubscriber : public rclcpp::Node
{
public:
  DistanceSubscriber()
  : Node("cpp_distance_subscriber")
  {
    subscription_ = create_subscription<std_msgs::msg::Float32>(
      "/turtle_distance", 10, [this](std_msgs::msg::Float32::SharedPtr msg) {
        RCLCPP_INFO(get_logger(), "distance: %.3f", msg->data);
      });
  }

private:
  rclcpp::Subscription<std_msgs::msg::Float32>::SharedPtr subscription_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<DistanceSubscriber>());
  rclcpp::shutdown();
  return 0;
}
