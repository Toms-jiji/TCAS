TCAS SYSTEM
-----------

Connect RC522 to 2 RPi (one each; no need to connect interrupt pin)
Use the rfid_writer.py to program rfid cards according to the test cased (may need to change variables in kavach_server_rpi.py, will be prompted by the rfid_writer.py program while programming)
Run Client programs on two RPi's and the server on a laptop (tested in linux machine, may need to intall additional packages for rfid and other libraries)
Verify test cases

NOTE: Please view code in editors like vscode for easy lookup


Main Code:
----------
    |->   kavach_client_rpi1.py -> Code to be run on rpi1       -> includes the rfid portion as well
    |->   kavach_client_rpi2.py -> Code to be run on rpi2       -> includes the rfid portion as well
    |->   kavach_server_rpi.py  -> Code with ip of rpi
    |->   rfid_writer.py        -> Code to write data to rfid cards based on test cases

Extra Code: (can be used to test scalability of code/algorithm)
------------
    |->   kavach_client.py (only basic features with random data)     -> Clients and test case emulator     -> Loopback address used
    |->   kavach_server.py (only basic features with random data)     -> For clients and test case emulator -> Server code with loopback address 


Features:
---------
    |-> Modified UDP used
    |    |-> -> To reduce packet overhead
    |-> ACKs for every data transmission
    |    |-> Special ACKS for STOP Messages to trains
    |    |-> Retransmission of data is ack is not received
    |-> Updation of train data only if the timestamp is larger than the one stored in database
    |    |-> Used to avoid packet retramission attacks
    |-> Authentication of Trains and server using challenge, response Authentication
    |    |-> Server accepts data from train only if they have been authenticated
    |-> RFID Authentication to check tampered RFIDs
    |-> Encripted communication between trains and server
    |-> Sensing of trains which have not responded for a long time and isolation of that track
    |    |->stopping other trains in that same track to avoid risk of collision
    |-> CRC checking for bit errors
    |    |-> Accepts data only if CRC passes
    |-> Head on collision
    |    |->Fixed collision distance    ->  minimum distance between trains is hardcoded and fixed
    |    |->Variable collision distance ->  minimum distance between trains computed on the fly based on relative speed of the trains
    |-> Tail end collision 
    |    |->Fixed collision distance    ->  minimum distance between trains is hardcoded and fixed
    |    |->Variable collision distance ->  minimum distance between trains computed on the fly based on relative speed of the trains
    |    |->only back train is stopped  ->  that too only if it is slower than the front train in case of variable collision distance
    |-> Case when trains are going in opposite direction
    |-> Trains in loop line
    |-> Stopped Trains
    |-> Trains at a station but not reached platform
    |-> Trains at a station and reached platform
    |-> trains running on different tracks (UP and DOWN tracks)
    |-> flushing of train data who have reached their destination (i.e reached parking space)
    |-> Measurement of RTT and transmission of that at the server. Can be later used to make a heat map to detect location of poor network
    |-> Efficient and scalable code
         |-> Linked List implementation of train database
         |-> Multi threaded, Thread safe and multiport implementation
