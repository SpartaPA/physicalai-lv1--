"""Publish the turtle's distance from the origin."""

import math

import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from rcl_interfaces.msg import SetParametersResult
from rclpy.qos import qos_profile_sensor_data
from std_msgs.msg import Float32
from turtlesim.msg import Pose


class DistancePublisher(Node):
    """Convert the latest turtle pose into a distance at 10 Hz."""

    def __init__(self):
        super().__init__('distance_publisher')

        self.declare_parameter('publish_rate', 10.0)
        self.declare_parameter('use_sensor_qos', False)
        publish_rate = self.get_parameter('publish_rate').value
        if publish_rate <= 0.0:
            self.get_logger().warning('publish_rate must be > 0; using 10 Hz')
            publish_rate = 10.0

        self.latest_x = 0.0
        self.latest_y = 0.0
        self.pose_received = False

        self.pose_subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10,
        )
        output_qos = (qos_profile_sensor_data
                      if self.get_parameter('use_sensor_qos').value else 10)
        self.distance_publisher = self.create_publisher(
            Float32,
            '/turtle_distance',
            output_qos,
        )

        self.publish_timer = self.create_timer(
            1.0 / publish_rate, self.publish_distance)
        self.add_on_set_parameters_callback(self.parameters_changed)

    def parameters_changed(self, parameters):
        """Apply a valid publish rate without restarting the node."""
        for parameter in parameters:
            if parameter.name == 'publish_rate':
                if parameter.value <= 0.0:
                    self.get_logger().warning('rejected publish_rate <= 0')
                    return SetParametersResult(successful=False)
                self.publish_timer.cancel()
                self.publish_timer = self.create_timer(
                    1.0 / parameter.value, self.publish_distance)
        return SetParametersResult(successful=True)

    def pose_callback(self, msg: Pose):
        """Store only the most recently received pose."""
        self.latest_x = msg.x
        self.latest_y = msg.y
        self.pose_received = True

    def publish_distance(self):
        """Calculate and publish distance from the timer callback."""
        if not self.pose_received:
            return

        distance_msg = Float32()
        distance_msg.data = math.hypot(self.latest_x, self.latest_y)
        self.distance_publisher.publish(distance_msg)


def main(args=None):
    """Run the distance publisher node."""
    rclpy.init(args=args)
    node = DistancePublisher()

    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
