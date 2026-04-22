import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/amira/test_urdf_gazebo/src/my_controller/install/my_controller'
