"""Draw regular polygons through a cancellable ROS action."""

import math
import time

import rclpy
from geometry_msgs.msg import Twist
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import ExternalShutdownException, MultiThreadedExecutor
from rclpy.node import Node
from turtle_interfaces.action import DrawPolygon


class PolygonActionServer(Node):
    def __init__(self):
        super().__init__('polygon_action_server')
        self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.server = ActionServer(
            self, DrawPolygon, 'draw_polygon', self.execute,
            goal_callback=self.goal_callback,
            cancel_callback=lambda _goal: CancelResponse.ACCEPT,
            callback_group=ReentrantCallbackGroup())

    def goal_callback(self, goal):
        if goal.sides < 3 or goal.side_length <= 0.0:
            self.get_logger().warning('rejected invalid polygon goal')
            return GoalResponse.REJECT
        return GoalResponse.ACCEPT

    def drive_for(self, goal_handle, linear, angular, seconds):
        command = Twist()
        command.linear.x = linear
        command.angular.z = angular
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            if goal_handle.is_cancel_requested:
                self.publisher.publish(Twist())
                return False
            self.publisher.publish(command)
            time.sleep(0.05)
        self.publisher.publish(Twist())
        return True

    def execute(self, goal_handle):
        goal = goal_handle.request
        speed = 1.0
        angular_speed = 1.0
        turn = 2.0 * math.pi / goal.sides
        feedback = DrawPolygon.Feedback()
        for side in range(goal.sides):
            if not self.drive_for(goal_handle, speed, 0.0,
                                  goal.side_length / speed):
                goal_handle.canceled()
                return DrawPolygon.Result(total_distance=side * goal.side_length)
            if not self.drive_for(goal_handle, 0.0, angular_speed,
                                  turn / angular_speed):
                goal_handle.canceled()
                return DrawPolygon.Result(total_distance=(side + 1) * goal.side_length)
            feedback.completed_sides = side + 1
            feedback.progress = float(side + 1) / goal.sides
            goal_handle.publish_feedback(feedback)
        goal_handle.succeed()
        return DrawPolygon.Result(total_distance=goal.sides * goal.side_length)


def main(args=None):
    rclpy.init(args=args)
    node = PolygonActionServer()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.publisher.publish(Twist())
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
