"""Launch turtlesim and the core turtle monitoring/action nodes."""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    params = os.path.join(
        get_package_share_directory('turtle_py'), 'config', 'params.yaml')
    return LaunchDescription([
        DeclareLaunchArgument('start_turtlesim', default_value='true'),
        DeclareLaunchArgument('start_turtle2_status', default_value='false'),
        Node(package='turtlesim', executable='turtlesim_node',
             name='turtlesim',
             condition=IfCondition(LaunchConfiguration('start_turtlesim'))),
        Node(package='turtle_py', executable='distance_publisher',
             name='distance_publisher', parameters=[params]),
        Node(package='turtle_py', executable='distance_subscriber',
             name='distance_subscriber', parameters=[params]),
        Node(package='turtle_py', executable='polygon_action_server',
             name='polygon_action_server'),
        Node(package='turtle_py', executable='distance_publisher',
             namespace='turtle2', name='distance_publisher',
             parameters=[params],
             remappings=[('/turtle1/pose', '/turtle2/pose'),
                         ('/turtle_distance', '/turtle2/turtle_distance')],
             condition=IfCondition(LaunchConfiguration('start_turtle2_status'))),
    ])
