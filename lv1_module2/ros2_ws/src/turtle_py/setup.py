import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'turtle_py'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='jourmain',
    maintainer_email='jourmain@todo.todo',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'distance_publisher = turtle_py.distance_publisher:main',
            'distance_subscriber = turtle_py.distance_subscriber:main',
            'square_driver = turtle_py.square_driver:main',
            'service_client = turtle_py.service_client:main',
            'rotate_action_client = turtle_py.rotate_action_client:main',
            'polygon_action_server = turtle_py.polygon_action_server:main',
            'polygon_action_client = turtle_py.polygon_action_client:main',
            'waypoint_publisher = turtle_py.waypoint_publisher:main',
            'tf_marker_publisher = turtle_py.tf_marker_publisher:main',
            'qos_probe = turtle_py.qos_probe:main',
        ],
    },
)
