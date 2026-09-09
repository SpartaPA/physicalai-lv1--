"""Drive a turtlesim turtle in a square and expose run/home services."""

import math
import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from std_srvs.srv import SetBool, Trigger
from turtlesim.msg import Pose


class SquareDriver(Node):
    def __init__(self):
        super().__init__('square_driver')
        self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)
        self.create_service(SetBool, 'set_driving', self.set_driving)
        self.create_service(Trigger, 'save_home', self.save_home)
        self.timer = self.create_timer(0.05, self.tick)
        self.enabled = True
        self.phase = 0
        self.phase_started = self.get_clock().now()
        self.latest_pose = None
        self.home = None

    def pose_callback(self, msg):
        self.latest_pose = msg

    def set_driving(self, request, response):
        self.enabled = request.data
        response.success = True
        response.message = 'driving enabled' if self.enabled else 'driving stopped'
        if not self.enabled:
            self.publisher.publish(Twist())
        return response

    def save_home(self, _request, response):
        if self.latest_pose is None:
            response.success = False
            response.message = 'no pose received'
        else:
            self.home = (self.latest_pose.x, self.latest_pose.y)
            response.success = True
            response.message = f'home saved at {self.home}'
        return response

    def tick(self):
        if not self.enabled or self.phase >= 8:
            self.publisher.publish(Twist())
            return
        elapsed = (self.get_clock().now() - self.phase_started).nanoseconds / 1e9
        turning = self.phase % 2 == 1
        duration = (math.pi / 2.0) / 1.0 if turning else 2.0 / 1.0
        if elapsed >= duration:
            self.phase += 1
            self.phase_started = self.get_clock().now()
            self.publisher.publish(Twist())
            return
        command = Twist()
        if turning:
            command.angular.z = 1.0
        else:
            command.linear.x = 1.0
        self.publisher.publish(command)


def main(args=None):
    rclpy.init(args=args)
    node = SquareDriver()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if rclpy.ok():
            node.publisher.publish(Twist())
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
