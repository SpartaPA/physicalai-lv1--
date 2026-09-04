"""Slow subscriber used to demonstrate history-depth message loss."""

import time
import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from rclpy.qos import QoSProfile, ReliabilityPolicy
from std_msgs.msg import Float32


class QosProbe(Node):
    def __init__(self):
        super().__init__('qos_probe')
        self.declare_parameter('delay', 0.3)
        self.declare_parameter('depth', 1)
        qos = QoSProfile(depth=self.get_parameter('depth').value)
        qos.reliability = ReliabilityPolicy.BEST_EFFORT
        self.count = 0
        self.create_subscription(Float32, '/turtle_distance', self.callback, qos)

    def callback(self, msg):
        self.count += 1
        self.get_logger().info(f'received #{self.count}: {msg.data:.3f}')
        time.sleep(self.get_parameter('delay').value)


def main(args=None):
    rclpy.init(args=args)
    node = QosProbe()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
