import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    package_path = get_package_share_directory("yahboomcar_nav")
    nav2_bringup_dir = get_package_share_directory("secure_patrol")

    nav2_param_path = LaunchConfiguration(
        "params_file", 
        default=os.path.join(
            package_path, "params", "rtabmap_nav_params.yaml"
        )
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            "params_file", 
            default_value=nav2_param_path,
            description="Full path to param file to load"
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                nav2_bringup_dir, "/launch", "/navigation_launch.py"
            ]),
            launch_arguments={      
                "params_file": nav2_param_path
            }.items(),
        ),
    ])
