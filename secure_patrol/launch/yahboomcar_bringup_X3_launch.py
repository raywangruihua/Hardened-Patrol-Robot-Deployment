import os

from ament_index_python.packages import get_package_share_directory, get_package_share_path

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    if not os.getenv("PRINTED"):
        os.environ["PRINTED"] = "1"
        print("---------------------robot_type = x3---------------------")
    
    urdf_tutorial_path = get_package_share_path("yahboomcar_description")
    default_model_path = urdf_tutorial_path / "urdf/yahboomcar_X3.urdf"

    model_arg = DeclareLaunchArgument(
        name="model", 
        default_value=str(default_model_path),
        description="Absolute path to robot urdf file"
    )

    robot_description = ParameterValue(
        Command(["xacro ", LaunchConfiguration("model")]), value_type=str
    )

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        ros_arguments=["--enclave", "/robot_state_publisher/robot_state_publisher"],
        parameters=[
            {"robot_description": robot_description}
        ]
    )

    joint_state_publisher_node = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        ros_arguments=["--enclave", "/joint_state_publisher/joint_state_publisher"],
    )

    driver_node = Node(
        package="yahboomcar_bringup",
        executable="Mcnamu_driver_X3",
        ros_arguments=["--enclave", "/yahboom/mcnamu_driver_x3"],
    )

    base_node = Node(
        package="yahboomcar_base_node",
        executable="base_node_X3",
        ros_arguments=["--enclave", "/yahboom/base_node_x3"],
        parameters=[
            {
                "pub_odom_tf": False,
                "linear_scale_x": 1.0,
                "linear_scale_y": 1.0,
                "angular_scale": 1.0,
            }
        ]
    )

    imu_filter_config = os.path.join(
        get_package_share_directory("yahboomcar_bringup"),
        "param",
        "imu_filter_param.yaml"
    )

    imu_filter_node = Node(
        package="imu_filter_madgwick",
        executable="imu_filter_madgwick_node",
        ros_arguments=["--enclave", "/imu_filter_madgwick/imu_filter_madgwick"],
        parameters=[
            imu_filter_config,
        ]
    )

    ekf_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory("secure_patrol"), "launch"),
            "/ekf_x1_x3_launch.py"
    ]))

    return LaunchDescription([
        model_arg,
        joint_state_publisher_node,
        robot_state_publisher_node,
        driver_node,
        base_node,
        imu_filter_node,
        ekf_node,
    ])
