import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32

from secure_patrol.modules.voice_interaction_module import VoiceInteractionModule


class VoiceNode(Node):
    def __init__(self):
        super().__init__("voice_node")

        self.declare_parameter("port", "/dev/myspeech")
        self.declare_parameter("baudrate", 115200)

        port = self.get_parameter("port").value
        baudrate = self.get_parameter("baudrate").value

        self.voice_module = VoiceInteractionModule(port, baudrate)
        self._publisher = self.create_publisher(Int32, "/voice", 1)
        self.create_timer(0.1, self._poll)

        self.get_logger().info("Voice node initialised.")

    def _poll(self):
        """Poll voice interaction module for response."""
        cmd = self.voice_module.read()
        if cmd is not None:
            msg = Int32()
            msg.data = cmd
            self._publisher.publish(msg)
            self.get_logger().info(f"Voice command received: {cmd}.")

    def destroy_node(self):
        self.get_logger().info("Destroying voice node...")
        try:
            self.voice_module.disconnect()
        except Exception as e:
            self.get_logger().warn(f"Error disconnecting voice module: {e}")
        super().destroy_node()


def main():
    rclpy.init()
    node = None
    try:
        node = VoiceNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
