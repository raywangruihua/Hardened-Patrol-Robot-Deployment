import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2


class ScreenNode(Node):
    def __init__(self):
        super().__init__("screen_node")

        self._cv_bridge = CvBridge()
        self.create_subscription(Image, "/camera/color/image_raw", self._display, 10)

    def _display(self, msg: Image):
        """Convert and display ROS Image message every time
        a new frame arrives.
        """
        frame = self._cv_bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        cv2.imshow("Camera", frame)
        cv2.waitKey(1)

    def destroy_node(self):
        try:
            cv2.destroyAllWindows()
        except Exception:
            pass
        super().destroy_node()


def main():
    rclpy.init()
    node = ScreenNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
