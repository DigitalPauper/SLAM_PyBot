#define leftMotorCCW 5
#define leftMotorCW 6
#define motorEnable 7
#define rightMotorCCW 9
#define rightMotorCW 10
#define onboardLED 13
#define maxMessage 64 // this maximum byte length bufffer can be changed if needed

byte specialByte = 253; // this byte indicates that the following number will be added to 253 to make the true value
byte startMarker = 254; // this byte indicates the start of a message
byte endMarker = 255;   // this byte indicates the end of a message

//================

byte bytesRecvd = 0;  // Number of bytes read from the buffer
byte dataSentNum = 0; // Initial number of integers sent from PC (from message length character)

byte dataRecvCount = 0;     // Total number bytes of encoded message data
byte dataRecvd[maxMessage]; // Container for the incoming message data stripped of its header and message bytes

byte intDataCount = 0;    // Total number of decoded integers recieved (should == tempBuffer[1])
int newData[maxMessage];  // Container for the final decoded integers

byte tempBuffer[maxMessage]; // Container to store the incoming character values until they can be processed
byte dataTotalSend = 0;

boolean inProgress = false;
boolean allReceived = false;

int outArray[maxMessage];

int pause_value = 100;
int period = 1000;
unsigned long time_now = 0;

void setup()
{
    // Setup IO
    pinMode(onboardLED, OUTPUT);
    pinMode(motorEnable, OUTPUT);
    pinMode(leftMotorCCW, OUTPUT);
    pinMode(leftMotorCW, OUTPUT);
    pinMode(rightMotorCW, OUTPUT);
    pinMode(rightMotorCCW, OUTPUT);
    // Initialize IO states
    digitalWrite(motorEnable, LOW);
    analogWrite(leftMotorCCW, LOW);
    analogWrite(leftMotorCW, LOW);
    analogWrite(rightMotorCW, LOW);
    analogWrite(rightMotorCCW, LOW);
    digitalWrite(onboardLED, LOW); // Off
    // Start serial communication
    Serial.begin(115200);
    // take a timestamp as a start time
    time_now = millis();
    // non-blocking pause here until the timer runs out
    while (millis() < time_now + period)
    {
        // blink while waiting so we know its alive
        digitalWrite(onboardLED, HIGH);
        delay(100);
        digitalWrite(onboardLED, LOW);
        delay(100);
    }
    // Send the 'ready' handshake message
    debugToPC("Arduino Ready from Serial_PWM_Controller_v2.ino");
    // configure the incoming message buffer space
    for (byte i = 0; i < maxMessage; i++)
    {
        tempBuffer[i] = 0;
    }
}


//================


void loop()
{
    // potReading = map(analogRead(potentiometerInput), 0, 1023, 0, 255);

    getSerialData();
    if (allReceived)
    {
        // remove the start, end, and data length information from the recieved string of bytes in tempBuffer[bytesRecvd]
        stripMessageBytes();
        // processes the data that is in dataRecvd[]
        decodeHighBytes();

        // if message recieved was the correct length
        if (tempBuffer[2] == bytesRecvd)
        {
            // Update LEDs
            updateOutputs();
        }

        // encode and send the data that the Arduino parsed back
        // returnData(newData, intDataCount);

        // request new data
        requestData();
    }
}


//================


void updateOutputs()
{
    // if pwm commands are within 8bit limit
    if (newData[2] <= 255 && newData[4] <= 255)
    {
        // dir 0 is Reverse, 1 if Forward
        // newData[0] = Enable
        // newData[1] = Left Motor CCW Speed
        // newData[2] = Left Motor CW Speed
        // newData[3] = Right Motor CW Speed
        // newData[4] = Right Motor CCW Speed

        if (newData[0] == 1)
        {
            digitalWrite(motorEnable, HIGH);
            analogWrite(leftMotorCCW, newData[1]);
            analogWrite(leftMotorCW, newData[2]);
            analogWrite(rightMotorCW, newData[3]);
            analogWrite(rightMotorCCW, newData[4]);
            digitalWrite(onboardLED, HIGH); // On
        }
        else
        {
            digitalWrite(motorEnable, LOW);
            analogWrite(leftMotorCCW, LOW);
            analogWrite(leftMotorCW, LOW);
            analogWrite(rightMotorCW, LOW);
            analogWrite(rightMotorCCW, LOW);
            digitalWrite(onboardLED, LOW); // Off
        }
    }
}

//================

void getSerialData()
{
    // Receives data into tempBuffer[]
    //   saves the number of bytes that the PC said it sent - which will be in tempBuffer[1]dataRecvd[1]
    //   uses decodeHighBytes() to copy data from tempBuffer to dataRecvd[]dataRecvd[1]
    //   the Arduino program will then process the data within dataRecvd[]
    if (Serial.available() > 0)
    {
        byte x = Serial.read();
        if (x == startMarker)
        {
            bytesRecvd = 0;
            inProgress = true;
            // debugToPC("start received");
        }
        if (inProgress)
        {
            tempBuffer[bytesRecvd] = x;
            bytesRecvd++;
        }
        if (x == endMarker)
        {
            inProgress = false;
            allReceived = true;
            dataSentNum = tempBuffer[1]; // Store the initial number of integers sent form the PC (unencoded)
        }
    }
}

//============================

void stripMessageBytes()
{
    // Removed header information and start/end tags from the message and stores the resultant to the global placeholder
    dataRecvCount = 0;
    for (byte n = 3; n < bytesRecvd - 1; n++)
    { // 3 skips the start marker and the count bytes, -1 omits the end marker
        dataRecvd[dataRecvCount] = tempBuffer[n];
        dataRecvCount++; // count the total number of bytes transmitted to the Arduino
    }
}

//====================

void decodeHighBytes()
{
    // Message comes in as bytes that need to be converted to integers and possibly combind
    byte c = 0;
    intDataCount = -1;
    while (c <= dataRecvCount)
    {
        intDataCount++;
        if (dataRecvd[c] == specialByte)
        {
            byte k = 0;
            while (dataRecvd[c] == specialByte)
            {
                k++;
                c++;
            }
            newData[intDataCount] = ((specialByte * k) + dataRecvd[c]);
        }
        else
        {
            newData[intDataCount] = int(dataRecvd[c]);
        }
        c++;
    }
}

//====================

void requestData()
{
    // Writes a debug character and the message byte 255 to confirm ter arduino is ready for more
    Serial.write(startMarker);
    Serial.print(char(bytesRecvd)); // Tell the PC the total recieved byte count
    Serial.write(endMarker);
    allReceived = false;
}

//====================

// Returns the recieved byte array as is
// void returnData(byte messageLength) {
//   for(byte i = 0; i < (messageLength); i++) {
//     Serial.write(tempBuffer[i]);                                                  // dump the bytes from the tempBuffer as characters in a string
//   }
// }

void returnData(int outgoingMessage[], byte messageLength)
{
    // Writes a debug character and the message byte 255 to confirm ter arduino is ready for more
    encodeHighBytes(outgoingMessage, messageLength);
    int finalMessageCount = (dataTotalSend + 4); // message length of the final message including totals and tags
    Serial.write(startMarker);
    Serial.write(messageLength);     // total number of unencoded ints
    Serial.write(finalMessageCount); // final sum (totals and tags)
    for (byte i = 0; i < (dataTotalSend); i++)
    {
        Serial.write(outArray[i]); // dump the bytes from the tempBuffer as characters in a string
    }
    Serial.write(endMarker);
}

//====================

void encodeHighBytes(int dataToPC[], byte dataLength)
{
    outArray[maxMessage];
    dataTotalSend = -1; // to accomidate incrementation at the top of the loop to not overflow
    byte i = 0;
    int encodingTotal = 0;
    int remainder = 0;
    while (i <= dataLength)
    {
        dataTotalSend++;
        if (dataToPC[i] >= specialByte)
        {
            encodingTotal = dataToPC[i] / specialByte;
            remainder = dataToPC[i] % specialByte;
            for (byte x = 0; x < encodingTotal; x++)
            {
                outArray[dataTotalSend] = specialByte;
                dataTotalSend++;
            }
            outArray[dataTotalSend] = remainder;
        }
        else
        {
            outArray[dataTotalSend] = dataToPC[i];
        }
        i++;
    }
}

//====================

void debugToPC(char arr[])
{
    byte nb = 0; // Message length = 0 indicates that this is a Debug message
    Serial.write(startMarker);
    Serial.write(nb);
    Serial.print(arr);
    Serial.write(endMarker);
}

//=========================

void blinkLED(byte numBlinks)
{
    for (byte n = 0; n < numBlinks; n++)
    {
        digitalWrite(onboardLED, HIGH);
        delay(pause_value - 50);
        digitalWrite(onboardLED, LOW);
        delay(pause_value);
    }
}

//=========================
