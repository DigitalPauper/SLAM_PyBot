#!/usr/bin/env python

import numpy as np
from adafruit_rplidar import RPLidar
from time import sleep
import socket
from math import floor

# Setup the RPLidar
PORT_NAME = "/dev/ttyUSB0"
lidar = RPLidar(None, PORT_NAME, timeout=3)


lidar.stop_motor()
print("Starting LiDAR Publisher")
sleep(1)
lidar.start_motor()
print("Press CTRL + C to stop LiDAR Publisher")



# TCP_IP = '127.0.0.1'
# Port to forward lidar data to
# TCP_IP = '137.168.1.107'
TCP_IP = '192.168.1.7'
TCP_PORT = 5005
# rough calculated buffer size: 2896 bytes
# increased to (2^10)+(2^11)
BUFFER_SIZE = 3072

# used to scale data to fit on the screen
max_distance = 0

tilt = 0
frame_count = 0

scan_data = [0] * 360
data = ""

def process_data(data):
    print("\n")
    print(f"Frame {frame_count}")
    # print(len(data))
    print(data)


def sendMsg(str):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.send(str.encode())
    data = s.recv(BUFFER_SIZE)
    s.close()
    return data


if __name__ == "__main__":
    while 1:
        try:
            for scan in lidar.iter_scans():
                for (_, angle, distance) in scan:
                    scan_data[min([359, floor(angle)])] = distance
                data_string = ";".join(map(str, scan_data))
                frame_count = frame_count + 1
                # transform the dataset into a ; seperated string
                data = sendMsg(data_string)
        except Exception as e:
            print(f"\nExiting: {e}\n")
            lidar.stop()
            lidar.stop_motor()
            lidar.disconnect()
    lidar.stop()
    lidar.stop_motor()
    lidar.disconnect()