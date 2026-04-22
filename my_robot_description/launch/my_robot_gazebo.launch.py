import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import xacro

def generate_launch_description():

    pkg = get_package_share_directory('my_robot_description')
    xacro_file = os.path.join(pkg, 'urdf', 'ros_shuttle.urdf.xacro')
    robot_description = xacro.process_file(xacro_file).toxml()

    return LaunchDescription([

        SetEnvironmentVariable(
            name='GZ_SIM_RESOURCE_PATH',
            value=os.path.join(pkg, '..')
        ),

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': robot_description,
                'use_sim_time': True
            }]
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(get_package_share_directory('ros_gz_sim'),
                             'launch', 'gz_sim.launch.py')
            ),
            launch_arguments={'gz_args': 'empty.sdf -r'}.items()
        ),

        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
            output='screen'
        ),

        Node(
            package='ros_gz_sim',
            executable='create',
            arguments=['-topic', 'robot_description',
                       '-name', 'ros_shuttle',
                       '-z', '0.05'],
            output='screen'
        ),

        TimerAction(period=15.0, actions=[
            Node(
                package='my_controller',
                executable='odom_publisher',
                output='screen'
            ),
            Node(
                package='my_controller',
                executable='controller_node',
                output='screen'
            ),
        ]),
    ])