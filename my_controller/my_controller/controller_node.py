import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64MultiArray
import math

# ── Robot Physical Parameters ──────────────────────────────────────
# Measure these from your URDF joint origins
WHEEL_RADIUS = 0.0175   # meters — from your inertia z-offset (~0.00875 * 2)
# Half the distance between X-wheel pairs (for rotation contribution)
LX = 0.26              # ~distance from center to X-wheel axis (m)
LY = 0.30              # ~distance from center to Y-wheel axis (m)


class OmniController(Node):
    """
    Subscribes to /cmd_vel (Twist).
    Computes per-wheel velocities using omni kinematics.
    Publishes to /wheel_velocity_controller/commands (Float64MultiArray).

    Joint order: [x1, x2, x3, x4, y1, y2, y3, y4]
    X-wheels drive in the robot's X direction.
    Y-wheels drive in the robot's Y direction.
    Both groups contribute to rotation (angular.z).
    """

    def __init__(self):
        super().__init__('omni_controller')

        self.cmd_sub = self.create_subscription(
            Twist, '/cmd_vel', self.cmd_vel_callback, 10)

        self.wheel_pub = self.create_publisher(
            Float64MultiArray,
            '/wheel_velocity_controller/commands', 10)

        self.get_logger().info('OmniController started. Waiting for /cmd_vel...')

    def cmd_vel_callback(self, msg: Twist):
        vx = msg.linear.x   # forward/backward (m/s)
        vy = msg.linear.y   # strafe left/right (m/s)
        wz = msg.angular.z  # rotation (rad/s)

        # Convert linear velocities to wheel angular velocities (rad/s)
        # X-axis wheels: driven by vx and rotation
        # The rotation contribution uses the Y-distance to the wheel
        vx_wheel = vx / WHEEL_RADIUS
        vy_wheel = vy / WHEEL_RADIUS
        rot_x = (wz * LY) / WHEEL_RADIUS  # rotation felt by X-wheels
        rot_y = (wz * LX) / WHEEL_RADIUS  # rotation felt by Y-wheels

        # Sign convention matches your URDF joint origins
        # Review joint positions to verify sign for your robot geometry
        wheel_x1 =  vx_wheel + rot_x   # front-right X-wheel
        wheel_x2 =  vx_wheel - rot_x   # front-left X-wheel
        wheel_x3 =  vx_wheel - rot_x   # rear-left X-wheel
        wheel_x4 =  vx_wheel + rot_x   # rear-right X-wheel

        wheel_y1 =  vy_wheel + rot_y   # front-right Y-wheel
        wheel_y2 =  vy_wheel - rot_y   # front-left Y-wheel
        wheel_y3 =  vy_wheel - rot_y   # rear-left Y-wheel
        wheel_y4 =  vy_wheel + rot_y   # rear-right Y-wheel

        cmd = Float64MultiArray()
        cmd.data = [
            wheel_x1, wheel_x2, wheel_x3, wheel_x4,
            wheel_y1, wheel_y2, wheel_y3, wheel_y4
        ]
        self.wheel_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = OmniController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()