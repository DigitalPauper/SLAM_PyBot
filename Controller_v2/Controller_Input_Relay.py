#!/usr/bin/env python

import socket
import serial, time, math
# import numpy as np

# Made to communicate with Serial_PWM_Controller_v2.ino

### USER DEFINED PARAMETERS ###
# arduinoPort = "/dev/ttyACM0"                                                      # Linux Machines: May need to be changed from /dev/ttyACM0 to /dev/ttyACM1
arduinoPort = "COM7"                                                              # Windows Machines: Configure to Arduino IDE detected port
baudRate = 115200
debug = False
TCP_IP = ''
TCP_PORT = 5005
BUFFER_SIZE = 2880  # Size of the 360 degree lidar array of 8 byte elements
###  END OF PARAMETERS ###

# Special message tags
specialByte = 253
startMarker = 254
endMarker = 255

# Example Message: {254,[initialLength][finalLength],[(1/0),(1/0),(Left Motor Speed),(1/0),(Right Motor Speed)],255}


def waitForArduino():
    # wait until the Arduino sends 'Arduino Ready' - allows time for Arduino reset
    # it also ensures that any bytes left over from a previous message are discarded
    global endMarker
    arduinoReady = True
    msg = ""
    print("Waiting for response")
    while arduinoReady:
        msg = recvFromArduino()
        if "Arduino Ready" in msg:
            arduinoReady = False
    # END function


def sendToArduino(intArray):
    intermediateIntList = []
    intermediateIntList = encodeHighBytes(intArray)
    headerList = [startMarker, len(intArray), len(intermediateIntList)+4]
    intermediateIntList = headerList + intermediateIntList
    intermediateIntList.append(endMarker)
    if debug:
        print("   Outgoing data:", intermediateIntList)
    for integer in intermediateIntList:
        # Concatenate the list of characters into a string of characters
        ser.write(bytes([integer]))
    return(intermediateIntList)
    # END function


def encodeHighBytes(inList):
    global specialByte
    outputList = []
    for integer in range(0,len(inList)):
        if (inList[integer] >= specialByte):
            encodedTotal = int(math.floor(inList[integer]/specialByte))
            remainder = int(math.floor(inList[integer]%specialByte))
            for _ in range(0,encodedTotal):
                outputList.append(specialByte)
            outputList.append(remainder)
        else:
            outputList.append(inList[integer])
    return(outputList)
    # END function


def decodeHighBytes(inList):
    global specialByte
    n = 0
    outList = []
    messageLength = len(inList)
    while (n < messageLength):
        if (ord(inList[n]) == specialByte):
            c = 0
            while(ord(inList[n]) == specialByte):
                # Count the number of special characters in a row
                n += 1
                c += 1
            # Append the multiple plus the trailing remainder 
            outList.append((c*253)+ord(inList[n]))
        else:
            # Otherwise simply store the character as the next entry
            outList.append(ord(inList[n]))                 
        n += 1
    return(outList[2:])
    # END function


def decodeDebugMessage(inList):
    recieved_message = ""
    for i in range(1,len(inList)):
        recieved_message = recieved_message + inList[i].decode("utf-8")
    return(recieved_message)
    # END function


def recvFromArduino():
    global waitingForReply
    waitForMessage = True
    incoming_message = []
    while waitForMessage:
        incomingByte = ser.read()
        if incomingByte:
            if ord(incomingByte) == 254:
                # Start of the message
                pass
            elif ord(incomingByte) == 255:
                # End of the message
                if ord(incoming_message[0]) == 0:
                    decodedMessage = decodeDebugMessage(incoming_message)
                    print("   Recieved Debug Message:", decodedMessage)
                    pass
                elif len(incoming_message) == 1:
                    decodedMessage = decodeHighBytes(incoming_message)
                    # print("\n   Arduino requests more data")
                    waitingForReply = False
                else:
                    decodedMessage = decodeHighBytes(incoming_message)
                    if debug:
                        print("   Recieved Message:", decodedMessage)
                    pass
                waitForMessage = False
                pass
            else:
                incoming_message.append(incomingByte)
    return decodedMessage
    # END function



###########################
#   PROGRAM BEGINS HERE
###########################

if __name__ == '__main__':
    start_time = time.time()
    ser = serial.Serial(arduinoPort, baudRate)
    previous_time = time.time()
    waitForArduino()
    time_difference = time.time() - previous_time
    outgoing_times = []
    incoming_times = []
    waitingForReply = False
    print("Arduino response took", time_difference ,"seconds\n")

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.bind((TCP_IP, TCP_PORT))
    soc.listen(1)
    conn, addr = soc.accept()
    print ('Connection address:', addr, "\n")
    while True:
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
                    if debug:
                        print(f' Recieved instruction: {controller_data}')
                    previous_time = time.time()                             # Timestamp taken for the sake of comparason
                    intList = sendToArduino(controller_data)                       # Output a copy of testData and return the outgoing data generated
                    current_time = time.time()                              # New timestamp
                    outgoing_times.append(current_time - previous_time)     # Store the difference to track time to send
                    #time.sleep(0.005)
                    waitingForReply = True
                    while(waitingForReply):
                        if ser.inWaiting:
                            previous_time = time.time()                             # Timestamp taken for the sake of comparason
                            recvFromArduino()                                       # Wait for response
                            current_time = time.time()                              # New timestamp
                            incoming_times.append(current_time - previous_time)     # Store the difference to track time to recieve

            conn.send(data)  # echo
            soc.listen(1)
            conn, addr = soc.accept()
        except KeyboardInterrupt:
            print("\nExiting: User interrupt")
            if debug:
                print("\n===========\n")
                averageOut = math.fsum(outgoing_times)/len(outgoing_times)
                print("Average Outgoing Message Time [", (averageOut), "](s)")
                print(" Frequency [", (1/averageOut), "](Hz)\n")
                averageIn = math.fsum(incoming_times)/len(incoming_times)
                print("Average Incoming Message Time [", (averageIn), "](s)")
                print(" Frequency [", (1/averageIn), "](Hz)\n")
            time.sleep(0.3)
            ser.close
            conn.close()
            break