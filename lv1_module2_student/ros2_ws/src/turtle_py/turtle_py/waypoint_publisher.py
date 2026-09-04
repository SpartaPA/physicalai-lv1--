"""Publish a durable list of example waypoints."""

import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from turtle_interfaces.msg import Waypoint, WaypointList


class WaypointPublisher(Node):
    def __init__(self):
        super().__init__('waypoint_publisher')
        self.declare_parameter('transient_local', True)
        qos = QoSProfile(depth=1)
        qos.reliability = ReliabilityPolicy.RELIABLE
        qos.durability = (
            DurabilityPolicy.TRANSIENT_LOCAL
            if self.get_parameter('transient_local').value
            else DurabilityPolicy.VOLATILE)
        self.publisher = self.create_publisher(WaypointList, '/waypoints', qos)
        self.timer = self.create_timer(0.5, self.publish_once)

    def publish_once(self):
        msg = WaypointList()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'world'
        points = [
            (2.0, 2.0, 'A'),
            (8.0, 2.0, 'B'),
            (8.0, 8.0, 'C'),
            (2.0, 8.0, 'D'),
        ]
        msg.waypoints = [Waypoint(x=x, y=y, tolerance=0.2, label=label)
                         for x, y, label in points]
        self.publisher.publish(msg)
        self.get_logger().info('published 4 durable waypoints')
        self.timer.cancel()


def main(args=None):
    rclpy.init(args=args)
    node = WaypointPublisher()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
