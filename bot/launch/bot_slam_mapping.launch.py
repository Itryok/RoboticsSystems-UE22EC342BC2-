import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription,DeclareLaunchArgument, LogInfo
from launch.conditions import UnlessCondition
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from nav2_common.launch import HasNodeParams
import xacro

def generate_launch_description():
    robotXacroName = 'diff_drive_bot'  # Has to match with robot name in xacro file
    namePackage = 'bot'
    modelFileRelativePath = 'urdf/bot.xacro'
    pathModelFile = os.path.join(get_package_share_directory(namePackage), modelFileRelativePath)
    robotDescription = xacro.process_file(pathModelFile).toxml()

    # Path to the custom world file in your package's 'worlds' folder
    world_file = 'obstacles.sdf'  # Name of your custom world file
    world_path = os.path.join(
        get_package_share_directory(namePackage), 'worlds', world_file
    )

    # Launch Gazebo with the custom world
    gazebo_rosPackageLaunch = PythonLaunchDescriptionSource(
        os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
    )
    gazeboLaunch = IncludeLaunchDescription(
        gazebo_rosPackageLaunch,
        launch_arguments={
            'gz_args': f'-r -v4 {world_path}',  # Load the custom world
            'on_exit_shutdown': 'true'
        }.items()
    )
    

    # Spawn the robot in Gazebo
    spawnModelNodeGazebo = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', robotXacroName,
            '-topic', 'robot_description',
            '-x', '1.0',  # X position
            '-y', '2.0',  # Y position
            '-z', '0.5'   # Z position
        ],
        output='screen',
    )

    # Robot state publisher
    nodeRobotStatePublisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robotDescription, 'use_sim_time': True}],
    )

    # Bridge parameters
    bridge_params = os.path.join(
        get_package_share_directory(namePackage),
        'params',
        'bridge_params.yaml'
    )

    # Start Gazebo ROS bridge
    start_gazebo_ros_bridge_cmd = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '--ros-args',
            '-p',
            f'config_file:={bridge_params}',
        ],
        output='screen',
    )
    
    rviz_config_file = os.path.join(
        get_package_share_directory(namePackage), 'config', 'bot_config.rviz'
    )
    
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file],
    )
    
    use_sim_time = LaunchConfiguration('use_sim_time')
    params_file = LaunchConfiguration('params_file')
    default_params_file = os.path.join(get_package_share_directory("bot"),
                                        'params', 'mapper_params_online_async.yaml')

    declare_use_sim_time_argument = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation/Gazebo clock')
    declare_params_file_cmd = DeclareLaunchArgument(
        'params_file',
        default_value=default_params_file,
        description='Full path to the ROS2 parameters file to use for the slam_toolbox node')
    
    has_node_params = HasNodeParams(source_file=params_file,
                                    node_name='slam_toolbox')

    actual_params_file = PythonExpression(['"', params_file, '" if ', has_node_params,
                                        ' else "', default_params_file, '"'])

    log_param_change = LogInfo(msg=['provided params_file ',  params_file,
                                    ' does not contain slam_toolbox parameters. Using default: ',
                                    default_params_file],
                                    condition=UnlessCondition(has_node_params))

    start_async_slam_toolbox_node = Node(
        parameters=[
            actual_params_file,
            {'use_sim_time': use_sim_time}
        ],
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen')


    launchDescriptionObject = LaunchDescription()

    # Add actions to the launch description
    launchDescriptionObject.add_action(gazeboLaunch)
    launchDescriptionObject.add_action(spawnModelNodeGazebo)
    launchDescriptionObject.add_action(nodeRobotStatePublisher)
    launchDescriptionObject.add_action(start_gazebo_ros_bridge_cmd)
    launchDescriptionObject.add_action(rviz_node)
    launchDescriptionObject.add_action(declare_use_sim_time_argument)
    launchDescriptionObject.add_action(declare_params_file_cmd)
    launchDescriptionObject.add_action(log_param_change)
    launchDescriptionObject.add_action(start_async_slam_toolbox_node)
    return launchDescriptionObject