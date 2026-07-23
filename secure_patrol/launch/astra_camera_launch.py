import os

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import AnyLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    astra_camera_launch = IncludeLaunchDescription(
        AnyLaunchDescriptionSource(
            os.path.join(get_package_share_directory("secure_patrol"), "launch",
                         "astra_pro_plus.launch.xml")
        ),
    )

    return LaunchDescription([
        astra_camera_launch,
    ])
