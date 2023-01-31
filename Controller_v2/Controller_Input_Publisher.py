from inputs import get_gamepad
# from datetime import datetime
import socket

### USER SETABLE VARIABLES ###
debug = False
# between 0 and 255
deadband = 55
TCP_IP = '127.0.0.1'
# TCP_IP = '137.168.1.120'
# TCP_IP = '192.168.1.33'
TCP_PORT = 5005
BUFFER_SIZE = 1024
### END USER SETABLE VARIABLES ###

# Placeholder for the outgoing message
data = ""
# Direction and Speed Command
leftMotorCommand = 0
# Direction and Speed Command
rightMotorCommand = 0
# Outgoing Message Command Container
arduinoMessage = [0, 0, 0, 0, 0]
# User Override
user_override = False
start_debounce_counter = 0


def sendMsg(str):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.send(str.encode())
    data = s.recv(BUFFER_SIZE)
    s.close()
    return data
    # END Function


def scale(value, fromLow, fromHigh, toLow, toHigh):
    return (value - fromLow) * (toHigh - toLow) / (fromHigh - fromLow) + fromLow
    # END Function



###########################
#   PROGRAM BEGINS HERE
###########################
if __name__ == '__main__':
    while True:
        try:
            new_message = False
            events = get_gamepad()
            for event in events:
                # Left Stick 
                if event.code == 'ABS_Y':
                    # set the new message flag
                    new_message = True
                    # scale the command to 8 bit for the arduino to handle speed
                    leftMotorCommand = round(scale(abs(int(event.state)),0,32768,0,252))
                    # deadband control
                    if leftMotorCommand <= deadband:
                        leftMotorCommand = 0

                    # find the sign to determine direction to travel
                    if int(event.state) < 0:
                        # Reverse
                        arduinoMessage[1] = leftMotorCommand
                        arduinoMessage[2] = 0
                    else:
                        # Forward
                        arduinoMessage[1] = 0
                        arduinoMessage[2] = leftMotorCommand

                # Right Stick 
                if event.code == 'ABS_RY':
                    # set the new message flag
                    new_message = True
                    # scale the command to 8 bit for the arduino to handle speed
                    rightMotorCommand = round(scale(abs(int(event.state)),0,32768,0,252))
                    # deadband control
                    if rightMotorCommand <= deadband:
                        rightMotorCommand = 0

                    # find the sign to determine direction to travel
                    if int(event.state) < 0:
                        # Reverse
                        arduinoMessage[3] = 0
                        arduinoMessage[4] = rightMotorCommand
                    else:
                        # Forward
                        arduinoMessage[3] = rightMotorCommand
                        arduinoMessage[4] = 0

                if event.code == 'BTN_START':
                    start_debounce_counter += 1
                    if start_debounce_counter == 2:
                        # buttons register on click and unclick
                        user_override = not user_override
                        print(f'User Overrive: {user_override}')
                        if user_override:
                            # Enable the Arduino PWM Control
                            arduinoMessage = [1,0,0,0,0]
                            outgoingMessage = ";".join(map(str, arduinoMessage))
                            data = sendMsg(outgoingMessage)
                        else:
                            # Disable the Arduino PWM Control
                            arduinoMessage = [0,0,0,0,0]
                            outgoingMessage = ";".join(map(str, arduinoMessage))
                            data = sendMsg(outgoingMessage)
                        start_debounce_counter = 0

                if event.code == 'BTN_SELECT':
                    # Disable the Arduino PWM Control
                    arduinoMessage = [0,0,0,0,0]
                    outgoingMessage = ";".join(map(str, arduinoMessage))
                    data = sendMsg(outgoingMessage)
                    # Send the shutdown message to the subscriber
                    data = sendMsg(str(0))
                    raise KeyboardInterrupt

                # new event to send to the arduino
                if new_message and user_override:
                    # now = datetime.now()
                    # print(f'{now.hour}:{now.minute}:{now.second}:{str(now.microsecond)[:2]} message to arduino: {arduinoMessage}')
                    if debug:
                        print(f' Message to arduino: {arduinoMessage}')
                    outgoingMessage = ";".join(map(str, arduinoMessage))
                    data = sendMsg(outgoingMessage)
                    # unset the new message flag
                    new_message = False

        except KeyboardInterrupt:
            print("\nExiting: User interrupt")
            break
