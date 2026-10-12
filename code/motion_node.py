import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class MotionNode(Node):
    def __init__(self):
        super().__init__('motion_node')
        
        self.max_linear_speed = 1.0
        self.max_angular_speed = 1.0
        
        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10
        )
        
        self.get_logger().info('Motion Node started')
        self.get_logger().info('Listening to /cmd_vel')

    def cmd_vel_callback(self, msg):
        linear_x = msg.linear.x
        angular_z = msg.angular.z
        
        if abs(linear_x) > self.max_linear_speed:
            self.get_logger().warn(
                f'Linear speed limit exceeded: {linear_x:.2f} m/s. '
                f'Limiting to {self.max_linear_speed:.2f} m/s'
            )
            linear_x = max(
                -self.max_linear_speed,
                min(linear_x, self.max_linear_speed)
            )
            
        if abs(angular_z) > self.max_angular_speed:
            self.get_logger().warn(
                f'Angular speed limit exceeded: {angular_z:.2f} rad/s. '
                f'Limiting to {self.max_angular_speed:.2f} rad/s'
            )
            angular_z = max(
                -self.max_angular_speed,
                min(angular_z, self.max_angular_speed)
            )
            
        self.get_logger().info(
            f'Processed: linear.x={linear_x:.2f}, '
            f'angular.z={angular_z:.2f}'
        )

def main(args=None):
    rclpy.init(args=args)
    node = MotionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
