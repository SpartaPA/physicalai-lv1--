"""Send polygon goals and optionally cancel them for verification."""

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from turtle_interfaces.action import DrawPolygon


class PolygonClient(Node):
    def __init__(self):
        super().__init__('polygon_action_client')
        self.declare_parameter('sides', 3)
        self.declare_parameter('side_length', 1.0)
        self.declare_parameter('cancel_after', -1.0)
        self.client = ActionClient(self, DrawPolygon, 'draw_polygon')
        self.goal_handle = None
        self.cancel_timer = None

    def send(self):
        self.client.wait_for_server()
        goal = DrawPolygon.Goal()
        goal.sides = self.get_parameter('sides').value
        goal.side_length = self.get_parameter('side_length').value
        future = self.client.send_goal_async(goal, feedback_callback=self.feedback)
        future.add_done_callback(self.accepted)

    def accepted(self, future):
        self.goal_handle = future.result()
        if not self.goal_handle.accepted:
            self.get_logger().warning('polygon goal rejected')
            rclpy.shutdown()
            return
        self.goal_handle.get_result_async().add_done_callback(self.result)
        delay = self.get_parameter('cancel_after').value
        if delay > 0.0:
            self.cancel_timer = self.create_timer(delay, self.cancel)

    def feedback(self, message):
        feedback = message.feedback
        self.get_logger().info(
            f'sides={feedback.completed_sides}, progress={feedback.progress:.2f}')

    def cancel(self):
        self.cancel_timer.cancel()
        self.get_logger().info('cancel requested')
        self.goal_handle.cancel_goal_async()

    def result(self, future):
        wrapped = future.result()
        self.get_logger().info(
            f'status={wrapped.status}, total_distance='
            f'{wrapped.result.total_distance:.3f}')
        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    node = PolygonClient()
    node.send()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
