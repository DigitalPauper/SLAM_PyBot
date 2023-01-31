# SLAM_PyBot

This is a learning exercise to implement an entirely pythonic slam navigating robot. 

On Windows, this program depends on DS4W for PS4 controller compatability.

This robot will have bluetooth controller override to drive in FPV over a TCP/IP connection.
All low level control is achieved utilizing an arduino uno to drive the H bridge controller over a customizable serial interface.


This will run on the Jetson Nano 2Gb dev kit. 
Nano setup requires JetPack version 4.6, NOT 4.6.1. 
Attempting to boot 4.6.1 will yield the below error and boot loop:
"The installer encountered an unrecoverable error a desktop session will now be run so that you may investigate the problem or try installing again"

JetPack 4.6 can be found here: https://developer.nvidia.com/embedded/jetpack-sdk-46#collapseJetsonNano
And it's setup instructions can be found here: https://developer.nvidia.com/embedded/learn/get-started-jetson-nano-2gb-devkit#write


These programs were built on Python 3.9.12 utilizing the Zeth's Inputs 0.5 library and Roboticia's RPLidar 0.9.2 library.
https://pypi.org/project/inputs/
https://github.com/zeth/inputs
https://pypi.org/project/rplidar/
https://github.com/Roboticia/RPLidar
