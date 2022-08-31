#!/home/pi/.pyenv/versions/rospy3/bin/python

import rospy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

INTRO = 0
FOLLOW_CHECK = 1
TURN = 2

class SelfDrive:

    def __init__(self, publisher):
        self.publisher = publisher
        self.mod = INTRO

    def lds_callback(self, scan):
        turtle_vel = Twist()
        
        if self.mod == INTRO:
            if 0 < scan.ranges[0] < 0.25 or 0 < scan.ranges[30] < 0.25 or 0 < scan.ranges[-30] < 0.25:
                self.mod = FOLLOW_CHECK
            else:
                turtle_vel.linear.x = 0.18
        
        elif self.mod == FOLLOW_CHECK:
            if 0 < scan.ranges[0] < 0.25 or 0 < scan.ranges[30] < 0.25 or 0 < scan.ranges[-30] < 0.25:
                turtle_vel.angular.z = -1.8
            elif abs(scan.ranges[110] - scan.ranges[70]) > 0.02 and (scan.ranges[110] - scan.ranges[70]) > 0 \
                    or 0 < scan.ranges[90] < 0.1:
                turtle_vel.angular.z = -0.7
                turtle_vel.linear.x = 0.18
            elif abs(scan.ranges[110] - scan.ranges[70]) > 0.02 and (scan.ranges[110] - scan.ranges[70]) < 0 \
                    or scan.ranges[90] > 0.2:
                if scan.ranges[110] - scan.ranges[70] < -0.04 and scan.ranges[110] != 0:
                    self.mod = TURN
                turtle_vel.angular.z = 0.7
                turtle_vel.linear.x = 0.18
            else:
                turtle_vel.linear.x = 0.18
                
        elif self.mod == TURN:
            turtle_vel.angular.z = 1.5
            turtle_vel.linear.x = 0.15
            if 0 < scan.ranges[0] < 0.22 or 0 < scan.ranges[30] < 0.25 or 0 < scan.ranges[45] < 0.25:
                self.mod = FOLLOW_CHECK
                
        self.publisher.publish(turtle_vel)
    
def main():
    rospy.init_node('self_drive')
    publisher = rospy.Publisher('cmd_vel', Twist, queue_size=1)
    driver = SelfDrive(publisher)
    subscriber = rospy.Subscriber('scan', LaserScan,
                                  lambda scan: driver.lds_callback(scan))
    rospy.spin()


if __name__ == "__main__":
    main()

