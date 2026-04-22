import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import xacro

def generate_launch_description():

    pkg = get_package_share_directory('my_robot_description')
    xacro_file = os.path.join(pkg, 'urdf', 'ros_shuttle.urdf.xacro')
    robot_description = xacro.process_file(xacro_file).toxml()
    rviz_config = os.path.join(pkg, 'rviz', 'urdf_config.rviz')

    return LaunchDescription([

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': robot_description,
                'use_sim_time': False
            }]
        ),

        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            output='screen'
        ),

        # حساب الحركة من cmd_vel
        Node(
            package='my_controller',
            executable='controller_node',
            output='screen'
        ),

        # نشر الـ odom و TF
        Node(
            package='my_controller',
            executable='odom_publisher',
            output='screen'
        ),

        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', rviz_config],
            output='screen'
        ),
    ])