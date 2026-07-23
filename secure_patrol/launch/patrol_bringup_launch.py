"""Copied and edited from Yahboom source code.

Original: yahboomcar_nav navigation_rtabmap_launch.py
"""

import os

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    package_launch_path = os.path.join(get_package_share_directory("secure_patrol"), "launch")

    astra_camera_launch = IncludeLaunchDescription(PythonLaunchDescriptionSource([
        package_launch_path, "/astra_camera_launch.py"
    ]))

    laser_bringup_launch = IncludeLaunchDescription(PythonLaunchDescriptionSource([
        package_launch_path, "/laser_bringup_launch.py"
    ]))

    """TODO
    Launch additional blurred rtabmap node to improve localization during blurred mode
    """
    rtabmap_localization_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([package_launch_path, "/rtabmap_localization_launch.py"]),
        launch_arguments={"database_path": "~/lehack_ros2_ws/maps/map_unblurred.db"}.items()
    )

    rtabmap_nav_launch = IncludeLaunchDescription(PythonLaunchDescriptionSource([
        package_launch_path, "/rtabmap_nav_launch.py"
    ]))

    screen_node = Node(
        package="secure_patrol",
        executable="screen_node",
        name="screen_node",
        ros_arguments=["--enclave", "/secure_patrol/screen"],
        output="screen",
    )

    voice_node = Node(
        package="secure_patrol",
        executable="voice_node",
        name="voice_node",
        parameters=[{
            "port": "/dev/myspeech",
            "baudrate": 115200,
        }],
        ros_arguments=["--enclave", "/secure_patrol/voice"],
        output="screen",
    )

    return LaunchDescription([
        astra_camera_launch,
        screen_node,
        voice_node,
        TimerAction(period=2.0, actions=[laser_bringup_launch]),
        TimerAction(period=5.0, actions=[rtabmap_localization_launch]),
        TimerAction(period=15.0, actions=[rtabmap_nav_launch]),
    ])
