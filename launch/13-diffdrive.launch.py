# Software License Agreement (BSD License 2.0)
#
# Copyright (c) 2023, Metro Robots
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of Metro Robots nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    package_arg = DeclareLaunchArgument('urdf_package',
                                        description='The package where the robot description is located',
                                        default_value='urdf_sim_tutorial')
    model_arg = DeclareLaunchArgument('urdf_package_path',
                                      description='The path to the robot description relative to the package root',
                                      default_value='urdf/13-diffdrive.urdf.xacro')

    rvizconfig_arg = DeclareLaunchArgument(
        name='rvizconfig',
        default_value=PathJoinSubstitution([FindPackageShare('urdf_sim_tutorial'), 'rviz', 'odom_urdf.rviz']),
    )

    gazebo_launch = IncludeLaunchDescription(
        PathJoinSubstitution([FindPackageShare('urdf_sim_tutorial'), 'launch', 'gazebo.launch.py']),
        launch_arguments={
            'urdf_package': LaunchConfiguration('urdf_package'),
            'urdf_package_path': LaunchConfiguration('urdf_package_path')
        }.items(),
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        arguments=['-d', LaunchConfiguration('rvizconfig')],
    )

    # spawner waits/polls for the controller_manager service to exist before
    # loading -- unlike a raw `ros2 control load_controller` call, which fires
    # once immediately and silently fails if Gazebo hasn't finished spawning
    # the robot / bringing up controller_manager yet.
    load_joint_state_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '--controller-manager-timeout', '30'],
        output='screen',
    )
    load_head_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['head_controller', '--controller-manager-timeout', '30'],
        output='screen',
    )
    load_gripper_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['gripper_controller', '--controller-manager-timeout', '30'],
        output='screen',
    )

    load_dd_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_drive_base_controller', '--controller-manager-timeout', '30'],
        output='screen',
    )
    rqt_robot_steering_node = Node(
        package='rqt_robot_steering',
        executable='rqt_robot_steering',
        # Confirmed via `ros2 topic list -t`: /cmd_vel is geometry_msgs/msg/TwistStamped
        # on this setup. rqt_robot_steering already defaults to /cmd_vel, it just
        # publishes plain Twist by default -- only the message type needs overriding.
        parameters=[{
            'default_stamped': True,
        }],
    )
    return LaunchDescription([
        package_arg,
        model_arg,
        rvizconfig_arg,
        gazebo_launch,
        rviz_node,
        load_joint_state_controller,
        load_head_controller,
        load_gripper_controller,
        load_dd_controller,
        rqt_robot_steering_node
    ])
