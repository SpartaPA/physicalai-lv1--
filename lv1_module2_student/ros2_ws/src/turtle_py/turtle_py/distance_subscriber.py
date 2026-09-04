"""Warn when the turtle is farther than a configurable threshold."""

import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from rclpy.qos import qos_profile_sensor_data
from std_msgs.msg import Float32


class DistanceSubscriber(Node):
    def __init__(self):
        super().__init__('distance_subscriber')
        self.declare_parameter('warn_distance', 2.5)
        self.declare_parameter('best_effort', False)
        qos = (qos_profile_sensor_data
               if self.get_parameter('best_effort').value else 10)
        self.create_subscription(Float32, '/turtle_distance', self.callback, qos)

    def callback(self, msg):
        threshold = self.get_parameter('warn_distance').value
        if msg.data > threshold:
            self.get_logger().warning(
                f'distance {msg.data:.3f} exceeds {threshold:.3f}')


def main(args=None):
    rclpy.init(args=args)
    node = DistanceSubscriber()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
