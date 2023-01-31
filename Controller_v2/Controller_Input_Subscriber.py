#!/usr/bin/env python

import socket
import numpy as np

TCP_IP = ''
TCP_PORT = 5005
BUFFER_SIZE = 2880  # Size of the 360 degree lidar array of 8 byte elements

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
conn, addr = s.accept()
print ('Connection address:', addr)
while 1:
    try:
        data = conn.recv(BUFFER_SIZE)
        if data: 
            # data to np array
            # lidar_data = np.fromstring(data.decode(), dtype=float, sep=';')
            # data to list
            controller_data = list(map(int, data.decode().split(";")))
            if len(controller_data) == 1 and controller_data[0] == 0:
                raise KeyboardInterrupt
            else:
                print(f' Recieved instruction: {controller_data}')

        conn.send(data)  # echo
        s.listen(1)
        conn, addr = s.accept()
    except KeyboardInterrupt:
        print("\nExiting: User interrupt")
        conn.close()
        break