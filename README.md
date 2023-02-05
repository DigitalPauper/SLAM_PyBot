# SLAM_PyBot

This is a learning exercise to implement an entirely pythonic slam navigating robot built to run on the Jetson Nano 2Gb dev kit.   


On Windows, this program depends on [DS4W](https://ds4-windows.com/) for PS4 controller compatability.   



This robot will have bluetooth controller override to drive in FPV over a TCP/IP connection.
All low level control is achieved utilizing an arduino uno to drive the H bridge controller over a customizable serial interface.   





Nano setup requires JetPack version 4.6, **NOT** 4.6.1. 
Attempting to boot 4.6.1 will yield the below error and boot loop:
>"The installer encountered an unrecoverable error a desktop session will now be run so that you may investigate the problem or try installing again"   



[JetPack 4.6 can be found here](https://developer.nvidia.com/embedded/jetpack-sdk-46#collapseJetsonNano)

[And it's setup instructions can be found here](https://developer.nvidia.com/embedded/learn/get-started-jetson-nano-2gb-devkit#write)

[Wifi can be added with help form the Sparkfun tutorial here](https://learn.sparkfun.com/tutorials/adding-wifi-to-the-nvidia-jetson/all)   


Once setup, install Python 3.9 to the Ubuntu 18.04 image from the deadsnakes PPA repository.
```
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.9
```


These programs were built on Python 3.9.12 utilizing the Zeth's Inputs 0.5 library, Roboticia's RPLidar 0.9.2 library, and python3-serial.

>https://pypi.org/project/inputs/   |  https://github.com/zeth/inputs
>
>https://pypi.org/project/rplidar/  |  https://github.com/Roboticia/RPLidar

Add the necessary packages to run the Lidar, accept custom communications over serial, and process direct controller inputs.
```
sudo apt-get install python3-serial
pip3 install rplidar
pip3 install inputs
```   


Make sure to ensure that the Arduino is set to the right port in the relay code. Check that it is plugged in and recognized. On linux it should appear as ttyACM0 or ttyACM1.
```
ls /dev/ttyACM*
```


On running the relay, if the Nano encountes the following error change the port permissions so that all users may have read write access:
>Permission denied: '/dev/ttyACM0' could not open port
```
sudo chmod a+rw /dev/ttyACM0
```
