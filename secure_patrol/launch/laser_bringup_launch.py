"""Copied and edited from Yahboom source code.

Now only supports ROSMASTER X3 and A1 RPLIDAR
"""

import os

from launch import LaunchDescription
from launch_ros.actions import Node 
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    package_launch_path = os.path.join(get_package_share_directory("secure_patrol"), "launch")

    if not os.getenv("LASER_BRINGUP_PRINTED"):
        os.environ["LASER_BRINGUP_PRINTED"] = "1"
        print("\n-------- robot_type = x3, rplidar_type = a1 --------\n")

    bringup_x3_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            package_launch_path, "/yahboomcar_bringup_X3_launch.py"
    ]))

    lidar_a1_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory("secure_patrol"), "launch"), 
            "/sllidar_launch.py"
    ]))

    tf_base_link_to_laser = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="static_transform_publisher",
        arguments=[
            "--x", "0.0435", "--y", "5.258E-05", "--z", "0.11",
            "--roll", "3.14", "--pitch", "0", "--yaw", "0",
            "--frame-id", "base_link", "--child-frame-id", "laser",
        ],
        ros_arguments=["--enclave", "/tf2/static_transform_publisher"]
    )

    return LaunchDescription([
        bringup_x3_launch,
        lidar_a1_launch,
        tf_base_link_to_laser
    ])