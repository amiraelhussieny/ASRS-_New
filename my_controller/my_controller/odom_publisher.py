import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped, Twist
import tf2_ros
import math

class OdomPublisher(Node):
    def __init__(self):
        super().__init__('odom_publisher')

        self.odom_pub = self.create_publisher(Odometry, '/odom', 10)
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)

        self.sub = self.create_subscription(
            Twist, '/cmd_vel', self.cmd_vel_cb, 10)

        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.last_time = None
        self.vx = 0.0
        self.vy = 0.0
        self.wz = 0.0

        self.timer = self.create_timer(0.05, self.update_odom)

    def cmd_vel_cb(self, msg: Twist):
        self.vx = msg.linear.x
        self.vy = msg.linear.y
        self.wz = msg.angular.z

    def update_odom(self):
        now = self.get_clock().now()
        if self.last_time is None:
            self.last_time = now
            return

        dt = (now - self.last_time).nanoseconds * 1e-9
        self.last_time = now

        # Integrate pose
        self.x     += (self.vx * math.cos(self.theta) -
                       self.vy * math.sin(self.theta)) * dt
        self.y     += (self.vx * math.sin(self.theta) +
                       self.vy * math.cos(self.theta)) * dt
        self.theta += self.wz * dt

        stamp = now.to_msg()
        q_z = math.sin(self.theta / 2.0)
        q_w = math.cos(self.theta / 2.0)

        # TF: odom → base_link
        t = TransformStamped()
        t.header.stamp = stamp
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_link'
        t.transform.translation.x = self.x
        t.transform.translation.y = self.y
        t.transform.translation.z = 0.0
        t.transform.rotation.z = q_z
        t.transform.rotation.w = q_w
        self.tf_broadcaster.sendTransform(t)

        # /odom topic
        odom = Odometry()
        odom.header.stamp = stamp
        odom.header.frame_id = 'odom'
        odom.child_frame_id = 'base_link'
        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.orientation.z = q_z
        odom.pose.pose.orientation.w = q_w
        odom.twist.twist.linear.x = self.vx
        odom.twist.twist.linear.y = self.vy
        odom.twist.twist.angular.z = self.wz
        self.odom_pub.publish(odom)

def main(args=None):
    rclpy.init(args=args)
    node = OdomPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()