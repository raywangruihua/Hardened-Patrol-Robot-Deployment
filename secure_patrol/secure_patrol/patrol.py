import time
import rclpy
from nav2_simple_commander.robot_navigator import BasicNavigator
from geometry_msgs.msg import PoseStamped


def make_pose(navigator, x, y, w=1.0):
    p = PoseStamped()
    p.header.frame_id = "map"
    p.header.stamp = navigator.get_clock().now().to_msg()
    p.pose.position.x = x
    p.pose.position.y = y
    p.pose.orientation.w = w
    return p

def main():
    rclpy.init()
    nav = BasicNavigator()
    nav.waitUntilNav2Active(localizer="behavior_server")

    waypoints = [
        make_pose(nav, 0.0, 0.0),
        make_pose(nav, 2.0, 0.0),
        make_pose(nav, 1.0, 1.0),
    ]

    while True:
        nav.followWaypoints(waypoints)
        while not nav.isTaskComplete():
            time.sleep(1)


if __name__ == "__main__":
    main()
