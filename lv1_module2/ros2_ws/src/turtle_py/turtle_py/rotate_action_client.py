"""Call turtlesim's RotateAbsolute action with feedback and optional cancel."""

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from turtlesim.action import RotateAbsolute


class RotateClient(Node):
    def __init__(self):
        super().__init__('rotate_action_client')
        self.declare_parameter('target_angle', 3.14)
        self.declare_parameter('cancel_after', -1.0)
        self.client = ActionClient(self, RotateAbsolute,
                                   '/turtle1/rotate_absolute')
        self.goal_handle = None

    def send(self):
        self.client.wait_for_server()
        goal = RotateAbsolute.Goal()
        goal.theta = float(self.get_parameter('target_angle').value)
        future = self.client.send_goal_async(goal, feedback_callback=self.feedback)
        future.add_done_callback(self.goal_response)
        cancel_after = self.get_parameter('cancel_after').value
        if cancel_after > 0.0:
            self.create_timer(cancel_after, self.cancel)

    def feedback(self, message):
        self.get_logger().info(f'remaining: {message.feedback.remaining:.3f}')

    def goal_response(self, future):
        self.goal_handle = future.result()
        if not self.goal_handle.accepted:
            self.get_logger().warning('goal rejected')
            rclpy.shutdown()
            return
        self.goal_handle.get_result_async().add_done_callback(self.result)

    def cancel(self):
        if self.goal_handle is not None:
            self.get_logger().info('requesting cancellation')
            self.goal_handle.cancel_goal_async()

    def result(self, future):
        self.get_logger().info(f'action status: {future.result().status}')
        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    node = RotateClient()
    node.send()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
