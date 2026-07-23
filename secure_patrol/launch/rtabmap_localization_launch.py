from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    qos = LaunchConfiguration("qos")
    database_path = LaunchConfiguration("database_path")

    parameters={
          "frame_id": "base_footprint",
          "use_sim_time": False,
          "subscribe_rgbd": True,
          "subscribe_scan": True,
          "use_action_for_goal": True,
          "qos_scan": qos,
          "qos_image": qos,
          "qos_imu": qos,
          # RTAB-Map"s parameters should be strings:
          "Reg/Strategy": "1",
          "Reg/Force3DoF": "true",
          "RGBD/NeighborLinkRefining": "True",
          "Grid/RangeMin": "0.2", # ignore laser scan points on the robot itself
          "Optimizer/GravitySigma": "0" # Disable imu constraints (we are already in 2D)
    }

    remappings=[
          ("rgb/image", "/camera/color/image_raw"),
          ("rgb/camera_info", "/camera/color/camera_info"),
          ("depth/image", "/camera/depth/image_raw"),
          ("odom", "/odom")
        ]

    return LaunchDescription([
        # Launch arguments
        DeclareLaunchArgument(
            "qos",
            default_value="2",
            description="QoS used for input sensor topics"
        ),
        DeclareLaunchArgument(
            "database_path",
            default_value="~/.ros/rtabmap.db",
            description="Path to the RTAB-Map database file"
        ),

        # Nodes to launch
        Node(
            package="rtabmap_sync",
            executable="rgbd_sync",
            output="screen",
            parameters=[{
                "approx_sync": True,
                "approx_sync_max_interval": 0.01,
                "use_sim_time": False,
                "qos":qos,
            }],
            remappings=remappings,
            ros_arguments=["--enclave", "/rtabmap/rgbd_sync"],
        ),
        Node(
            package="rtabmap_slam",
            executable="rtabmap", 
            parameters=[
                parameters,
                {
                    "Mem/IncrementalMemory":"False",
                    "Mem/InitWMWithAllNodes":"True",
                    "database_path": database_path,
                }
            ],
            remappings=remappings,
            ros_arguments=["--enclave", "/rtabmap/rtabmap"],
        ),
    ])
