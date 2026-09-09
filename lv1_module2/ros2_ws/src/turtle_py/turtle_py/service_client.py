"""Call four built-in turtlesim services in sequence."""

import rclpy
from rclpy.node import Node
from std_srvs.srv import Empty
from turtlesim.srv import SetPen, Spawn, TeleportAbsolute


class TurtleServiceClient(Node):
    def __init__(self):
        super().__init__('turtle_service_client')

    def call(self, service_name, service_type, request):
        client = self.create_client(service_type, service_name)
        if not client.wait_for_service(timeout_sec=5.0):
            raise RuntimeError(f'{service_name} is unavailable')
        future = client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        if future.exception() is not None:
            raise future.exception()
        self.get_logger().info(f'{service_name}: {future.result()}')
        self.destroy_client(client)

    def run(self):
        teleport = TeleportAbsolute.Request(x=2.0, y=2.0, theta=0.0)
        pen = SetPen.Request(r=255, g=80, b=30, width=3, off=0)
        spawn = Spawn.Request(x=8.0, y=8.0, theta=0.0, name='turtle2')
        self.call('/turtle1/teleport_absolute', TeleportAbsolute, teleport)
        self.call('/turtle1/set_pen', SetPen, pen)
        self.call('/spawn', Spawn, spawn)
        self.call('/clear', Empty, Empty.Request())


def main(args=None):
    rclpy.init(args=args)
    node = TurtleServiceClient()
    try:
        node.run()
    except Exception as error:  # report failures without an unhandled traceback
        node.get_logger().error(str(error))
    finally:
        node.destroy_node()
        rclpy.shutdown()
