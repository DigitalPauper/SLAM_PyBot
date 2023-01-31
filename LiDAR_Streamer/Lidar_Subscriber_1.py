#!/usr/bin/env python

import socket
import numpy as np

TCP_IP = ''
TCP_PORT = 5005
BUFFER_SIZE = 3072  # Size of the 360 degree lidar array of 8 byte elements

print("\nStarting TCP/IP Subscriber\n")

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
                lidar_data = list(data.decode().split(";"))
                for i in range(0,len(lidar_data)):
                    if len(lidar_data[i]) == 0:
                        pass
                    else:                            
                        scan_data.append(list(map(float, lidar_data[i].split(","))))

                # scan_data contains the raw data from the lidar module
                # print(f'{scan_data[1][0]}  {scan_data[1][1]}  {scan_data[1][2]}')

            conn.send(data)  # echo
            s.listen(1)
            conn, addr = s.accept()
        except KeyboardInterrupt:
            print("\nExiting: User interrupt")
            conn.close()
            break


