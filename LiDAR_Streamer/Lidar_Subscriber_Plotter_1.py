#!/usr/bin/env python

import socket
from math import cos, sin, pi, floor, radians
import numpy as np
import matplotlib.pyplot as plt

TCP_IP = ''
TCP_PORT = 5005
BUFFER_SIZE = 3072  # Size of the 360 degree lidar array of 8 byte elements


frame_count = 0
plt_padding = 5

firstFrame = True
x0 = []
y0 = []

x = []
y = []
rangeX = [0,0]
rangeY = [0,0]

print("\nStarting TCP/IP Subscriber\n")


def process_data(recieved_data):
    global x
    global y
    lidar_data = list(recieved_data.decode().split(";"))
    for i in range(0,len(lidar_data)):
        if len(lidar_data[i]) == 0:
            pass
        else:
            point = list(lidar_data[i].split(","))
            data_point = []
            for j in range(0,len(point)):
                if len(point[j]) == 0:
                    data_point.append(float(0))
                else:
                    data_point.append(float(point[j]))
            scan_data.append(data_point)
    return scan_data



if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((TCP_IP, TCP_PORT))
    s.listen(1)
    conn, addr = s.accept()
    while 1:
        try:
            data = conn.recv(BUFFER_SIZE)
            if data: 
                scan_data = []
                x = []
                y = []

                current_data = process_data(data)

                for point in current_data:
                    if point[0]==15 and len(point) == 3:
                        newX = radians(point[2])*sin(radians(point[1]))
                        newY = radians(point[2])*cos(radians(point[1]))
                        x.append(newX)
                        y.append(newY)
                        if newX < rangeX[0]:
                            rangeX[0] = newX
                        if newX > rangeX[1]:
                            rangeX[1] = newX
                        if newY < rangeY[0]:
                            rangeY[0] = newY
                        if newY > rangeY[1]:
                            rangeY[1] = newY
                plt.clf()# set axes range
                plt.xlim(rangeX[0]-plt_padding, rangeX[1]+plt_padding)
                plt.ylim(rangeY[0]-plt_padding, rangeY[1]+plt_padding)
                plt.scatter(x, y)
                if not firstFrame:
                    plt.scatter(x0, y0)
                plt.pause(.00001)
                x0 = x
                y0 = y
                if firstFrame:
                    firstFrame = False
            conn.send(data)  # echo
            s.listen(1)
            conn, addr = s.accept()
        except KeyboardInterrupt:
            print("\nExiting: User interrupt")
            conn.close()
            break