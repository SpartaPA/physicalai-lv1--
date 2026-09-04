"""Broadcast world->turtle1 TF and visualize durable waypoints."""

import math

import rclpy
from geometry_msgs.msg import TransformStamped
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from tf2_ros import TransformBroadcaster
from turtlesim.msg import Pose
from turtle_interfaces.msg import WaypointList
from visualization_msgs.msg import Marker


class TfMarkerPublisher(Node):
    def __init__(self):
        super().__init__('tf_marker_publisher')
        self.broadcaster = TransformBroadcaster(self)
        self.marker_publisher = self.create_publisher(Marker, '/waypoint_markers', 10)
        self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)
        self.create_subscription(WaypointList, '/waypoints', self.waypoints_callback, 10)

    def pose_callback(self, pose):
        transform = TransformStamped()
        transform.header.stamp = self.get_clock().now().to_msg()
        transform.header.frame_id = 'world'
        transform.child_frame_id = 'turtle1'
        transform.transform.translation.x = float(pose.x)
        transform.transform.translation.y = float(pose.y)
        transform.transform.rotation.z = math.sin(pose.theta / 2.0)
        transform.transform.rotation.w = math.cos(pose.theta / 2.0)
        self.broadcaster.sendTransform(transform)

    def waypoints_callback(self, waypoint_list):
        if not waypoint_list.waypoints:
            self.get_logger().warning('empty waypoint list ignored')
            return
        marker = Marker()
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.header.frame_id = 'world'
        marker.ns = 'waypoints'
        marker.id = 0
        marker.type = Marker.SPHERE_LIST
        marker.action = Marker.ADD
        marker.scale.x = marker.scale.y = marker.scale.z = 0.25
        marker.color.r = 1.0
        marker.color.g = 0.3
        marker.color.a = 1.0
        for waypoint in waypoint_list.waypoints:
            from geometry_msgs.msg import Point
            marker.points.append(Point(x=waypoint.x, y=waypoint.y, z=0.0))
        self.marker_publisher.publish(marker)


def main(args=None):
    rclpy.init(args=args)
    node = TfMarkerPublisher()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
