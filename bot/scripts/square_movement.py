#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class SquareMovement(Node):
    def __init__(self):
        super().__init__('square_movement')
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.timer = self.create_timer(1.0, self.move_square)
        self.step = 0

    def move_square(self):
        twist = Twist()
        if self.step < 4:
            # Move forward
            twist.linear.x = 0.5  # Forward speed (m/s)
            twist.angular.z = 0.0
            self.get_logger().info('Moving forward')
        elif self.step < 5:
            # Stop before turning
            twist.linear.x = 0.0
            twist.angular.z = 0.0
            self.get_logger().info('Stopping before turn')
        elif self.step < 6:
            # Turn 90 degrees
            twist.linear.x = 0.0
            twist.angular.z = 1.57  # Angular velocity (rad/s) for 90 degrees in 1 second
            self.get_logger().info('Turning 90 degrees')
        else:
            # Reset step counter
            self.step = -1

        self.publisher.publish(twist)
        self.step += 1

def main(args=None):
    rclpy.init(args=args)
    square_movement = SquareMovement()
    rclpy.spin(square_movement)
    square_movement.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()