from setuptools import find_packages, setup
import os
from glob import glob
package_name = 'my_controller'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
    ('share/ament_index/resource_index/packages',
        ['resource/' + package_name]),
    ('share/' + package_name, ['package.xml']),
    # Add this if you have launch files in the control pkg:
    (os.path.join('share', package_name, 'launch'),
        glob('launch/*.xml')),
],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='amira',
    maintainer_email='amira@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
    'console_scripts': [
        'controller_node = my_controller.controller_node:main',
        'odom_publisher = my_controller.odom_publisher:main',

    ],
},
)
