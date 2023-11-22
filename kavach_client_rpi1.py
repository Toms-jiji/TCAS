import socket
import time
from datetime import datetime
import random
from cryptography.fernet import Fernet
from random import randint
import threading
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import signal
import sys

################################################################################################
#   Author: Toms Jiji Varghese                                                                 #
#   Date: 19/11/2023                                                                           #
#   Time: 11:49pm                                                                              #
#   Rev: 1.7                                                                                   #
#   GitHub: https://github.com/Toms-jiji/Kavach/tree/master                                    #
#                                                                                              #
#   Copyright (c) 2023 toms jiji varghese. ALL RIGHTS RESERVED.                                #
#   This code is the sole property of Toms Jiji Varghese and may not be copied, distributed,   #
#   or modified without the express written permission of Toms Jiji Varghese.                  #
################################################################################################ 

STOPPED_TRAINS = False                  #True for simulating stopped train and False for otherwise
TAIL_END_COLLISION = True               #True for simulating tail end collision and False for otherwise

ACK_MESSAGE_SERVER              = "ACK_from_server"     #Message used to verify ACKs from server
ACK_MESSAGE_CLIENT              = "ACK_from_client"     #Message used to verify ACKs from client
STOP_MESSAGE                    = "STOP STOP STOP"      #Message sent by server to stop train
CHALLENGE_FROM_CLIENT = "What is your professor's name" #Challenge message given by train/client
RESPONSE_TO_CLIENT    = "TVP"                           #Accepted response for Client's Challenge
CHALLENGE_FROM_SERVER = "What is your course name"      #Challenge sent by server to train 
RESPONSE_TO_SERVER    = "TCP/IP"                        #Accepted response to Server's Challenge
AUTH_TIMEOUT           = 1                              #Authentication Timeout time for ACKs
CRC_POLYNOMIAL      = 198 #max 8bit                     #CRC polynomial in integer from for CRC calculation
SERVER_PORT                     = 10000                 #Server's main port number
CLIENT_PORT                     = 11000                 #Client's main port number
RTT_SCALING_FACTOR              = 20                    #RTT scaling factor as RTT to reduce number of bits utilised while transmission by reducing resolution
SERVER_IP                       = "10.114.240.35"       #Server IP Address
TRANSMISSION_TIMEOUT            = 2                     #Time after which retransmission of packet takes place

WEEKDAY_START_OF_TRAIN          = 5                     #The day of week when the train started; used because there may be multiple trains with same train numebr running (eg. one started on Monday and other on Wednesday)
TRAIN_NUMBER                    = 1105                  #Train number
TRAIN_DIRECTION                 = 1                     #Direction of train; right now hard coded for ease of demonstration, but can be calculated from sequence of rfid scans

if(STOPPED_TRAINS==True):           
    SPEED                           = 0                 #If simulating stopped train then keep speed 0
else:
    SPEED                           = 50                

if (TAIL_END_COLLISION == True):
    SPEED                           = 150
    TRAIN_DIRECTION                 = 0                 # 0-> towards station1 ; 1-> towards station2

key = b'NaYMfYO0C8jy4fF1ImKOMobqqvq7FMlxDCIZDFIOShk='   #encryption key
global data_to_transmit                                 #variable used to store the data to be transmitted
fernet = Fernet(key)                                    #generate encryption object

reader = SimpleMFRC522()                                #initializing rfid reader
is_reading = True                                       #Start reading rfid if this variable is True
GPIO.setwarnings(False)                                 #Trunign of GPIO warnings 

class Train_node:                                       #Class used to create Linked List which is later used to store all train data
    def __init__(self, data_list=None):   #Total = 127bits
        if data_list is None:
            self.weekday             = None
            self.train_no        	 = None
        
            self.station1         	 = None
            self.station2  	      	 = None
            self.at_station_YN     	 = None
            self.reached_platform_YN = None
            self.platform_ID 	     = None
            self.platform_entry_YN	 = None
            self.branch_ID	 	     = None
            self.distance		     = None
            self.loop_line_YN	     = None
            self.loop_line_ID	     = None
            self.track_direction	 = None
            
            self.tx_time   		     = None
            self.speed     		     = None
            self.stop      		     = None
            self.direction 		     = None
            self.latency   		     = None
        
        else:
            self.weekday       	     = data_list[0] 			#3bits  -> used to store the weekday when train started
            self.train_no        	 = data_list[1]			    #16bits -> used to store the train number
            
            self.station1         	 = data_list[2]			    #14bits -> used to store station1 code 
            self.station2  	      	 = data_list[3]			    #14bits -> used to store station2 code
            self.at_station_YN     	 = data_list[4]		        #1bit   -> used to determine if train is at a station
            self.reached_platform_YN = data_list[5]	            #1bit   -> used to determine if train has reached a platform; if train is at a station
            self.platform_ID 	     = data_list[6]			    #5bits  -> used to uniquely identify every platform; if train is at a staion
            self.platform_entry_YN	 = data_list[7]	            #1bit   -> used to identify if train has entered a branch at a station leading to a particulat platform
            self.branch_ID	 	     = data_list[8]			    #6bits  -> used to identify branch of track at a station
            self.distance		     = data_list[9]			    #6bits  -> used to store distance from station1
            self.loop_line_YN	     = data_list[10]			#1bit   -> used to identify if train is in a loop line
            self.loop_line_ID	     = data_list[11]			#1bit   -> used to uniquely identify loopline entry and exit
            self.track_direction	 = data_list[12]		    #1bit   -> used to identify UP and DOWN tracks
            
            self.tx_time   		     = data_list[13]		    #20bits -> used to store time when the packet was transmitted
            self.speed     		     = data_list[14]            #8bits	-> Max is 200kmph and resolution is 1kmph
            self.stop      		     = data_list[15]			#1bit   -> 1=train is stopped else 0
            self.direction 		     = data_list[16]           	#1bit	-> 0-> towards station 1      1-> towards station 2
            self.latency   		     = data_list[17]            #10bits	-> used to store RTT
            self.next		         = None
    def show(self):                                             #Function used to print a linkedlist node (i.e a train data)
        now = datetime.now()
        weekday = int(now.isoweekday())
        hour = round((self.tx_time/weekday)//(60*60))           #Calulating time to be stored in packet
        min = round(((self.tx_time/weekday)%(60*60))//(60))
        sec = round(((self.tx_time/weekday)%(60*60))%(60))

        print("Train details are:")
        print("Weekday  	    	:",self.weekday)
        print("train_no  	    	:",self.train_no)
        
        print("station1  	    	:",self.station1)
        print("station2  	    	:",self.station2)
        print("at_station_YN  		:",self.at_station_YN)
        print("reached_platform_YN     :",self.reached_platform_YN)
        print("platform_ID  		:",self.platform_ID)
        print("platform_entry_YN  	:",self.platform_entry_YN)
        print("branch_ID    		:",self.branch_ID)
        print("distance  	    	:",self.distance)
        print("loop_line_YN  		:",self.loop_line_YN)
        print("loop_line_ID  		:",self.loop_line_ID)
        print("track_direction  	:",self.track_direction)
        print(f"tx_time                 : {hour}:{min}:{sec}")
        print("tx_time   	    	:",self.tx_time)
        print("speed     	    	:",self.speed)
        print("stop      	    	:",self.stop)
        print("direction 	    	:",self.direction)
        print("RTT (us)   	    	:",self.latency * RTT_SCALING_FACTOR)


#Function used to encrypt a message        
def encrypt_message(message):
    return fernet.encrypt(message.encode())

#Function used to decrypt a message
def decrypt_message(message):
    # Encode the message to bytes
    message_bytes = message

    # Decrypt the message
    decrypted_message = fernet.decrypt(message_bytes)

    # Return the decrypted message
    return decrypted_message.decode()

#function to print a packet
def print_packet(packet):
    size_array          = [3,16,14,14,1,1,5,1,6,6,1,1,1,20,8,1,1,10]     #Variable used to store number of bits used for each field
    packet = int(packet, 2)
    array = [None]*18   
    for i in range(0,18):                                       #Decoding the binary data into usedful data to be printed 
        array [17-i] = packet & ((2**(size_array[17-i]))-1)
        packet = packet >> (size_array[17-i])           
    Train = Train_node(array)   #creating a dummy node to store the data
    Train.show()                #printing the data in dummy node
    
#Function used to transmit data
def transmit(sock, data_to_transmit):
    # Send a message to the server
    packet_loss = 0
    while True:
        server_address = (SERVER_IP, SERVER_PORT)
        print("Sending...")
        start_ms = int(round(time.time() * 1000000))    #Start timer to calculate RTT
        sock.sendto(data_to_transmit, server_address)

        # Wait for a response from the server
        sock.settimeout(TRANSMISSION_TIMEOUT)
        try:
            data, server = sock.recvfrom(4096)
        except socket.timeout:                          #Did not receive any ack from server so retransmitting
            packet_loss += 1
            print("Server is not responding. Retransmitting data...")
            continue
        print("packet Loss: ",packet_loss)              #printing packet loss
        if ACK_MESSAGE_SERVER == decrypt_message(data): #checking the received data against reference message
            stop_ms = int(round(time.time() * 1000000)) #stoping the timer for RTT
            RTT = round((stop_ms-start_ms)/20)          #Calculating and storing the RTT
            print(decrypt_message(data))                #Printing the packet
            print("RTT: ",(RTT*20))                     #Printing the RTT
            break
        elif STOP_MESSAGE == decrypt_message(data):     #If message to STOP the train is received (by mistake on this port; other port is used for stop messages) then return None so that it can be detected  
            return None

        print('ACK from server is incorrect, retransmitting the data')
    
    print('ACK received from {}:{}'.format(server[0], server[1]))
    print(decrypt_message(data))
    return (RTT)                                        #Returning RTT

#Function to read RFID    
def rfid_read():
    # Hook the SIGINT
    signal.signal(signal.SIGINT, end_read)
    GPIO.setwarnings(False)                 #Turn of GPIO warnings
    GPIO.cleanup()

    try:
        id, data = reader.read()            #Read RFID
    finally:
        GPIO.cleanup()
    return data

# Capture SIGINT for cleanup
def end_read(signal, frame):
    global is_reading
    print('Ctrl+C captured, exiting')
    is_reading = False
    sys.exit()

#function to extract defined number of bits
def extract_bits(message, extract_bits, position):
    return (message >> message.bit_length()-extract_bits-position) & (2**(extract_bits)-1)

#function to decode rfid data and pack it in an array
def decode_rfid_data(message,RTT):
    now = datetime.now()
    weekday = int(now.isoweekday())

    current_time        = ((now.hour)*60*60 + (now.minute)*60 + (now.second))*weekday
    week_day            = WEEKDAY_START_OF_TRAIN                               #max 7
    train_no 		    = TRAIN_NUMBER
    at_station_YN 		= 0
    reached_platform_YN = 0
    platform_ID 		= 0
    platform_entry_YN 	= 0 
    branch_ID 		    = 0
    distance 		    = 0
    loop_line_YN 		= 0
    loop_line_ID 		= 0
    track_direction 	= 0
    tx_time 		    = current_time
    speed 			    = SPEED  
    stop 			    = 0                                     #max 1
    direction 		    = TRAIN_DIRECTION                                     #max 1
    latency 		    = RTT

    message = int(message)

    station1 		    = extract_bits(message, 14, 0)          #extracting bits corresponding to station1
    station2 	    	= extract_bits(message, 14, 14)
    if(station1 == station2):                                   #RFID card is at a station (not in parking space)
        at_station_YN 		= 1
        reached_platform_YN 	= extract_bits(message, 1, 28) 
        if (reached_platform_YN == 1):                          #RFID card is at a platform
            platform_ID 		= extract_bits(message, 5, 29)
            platform_entry_YN   = extract_bits(message, 1, 34)
        else:                                                   #RFID is not at a platform but a branch track at a station
            branch_ID 		    = extract_bits(message, 6,  29)
    else:
        distance 		    = extract_bits(message, 6,  28)
        loop_line_YN 		= extract_bits(message, 1,  34)
        loop_line_ID 		= extract_bits(message, 1,  35)
        track_direction 	= extract_bits(message, 1,  36)

    #array containing all packet data
    array		        = [week_day, train_no, station1, station2, at_station_YN, reached_platform_YN, platform_ID, platform_entry_YN, branch_ID, distance, loop_line_YN, loop_line_ID, track_direction, tx_time, speed, stop, direction, latency]
    size_array          = [3,16,14,14,1,1,5,1,6,6,1,1,1,20,8,1,1,10]
    string_array        = ""
    if array[17]>1023:
        array[17] = 1023    #trauncating RTT if it overflows (for safety)
    for i in range(0,18):
        string_array    = string_array + str(format(array[i], f"0{size_array[i]}b"))    #Convert all data in string format of binary
    return int(string_array,2)  #Return data in integer form

#function to check if data from RFID is valid
def check_data(data):
    try:
        data = int(str(data))
    except ValueError:
        return 0
    
    data = int(str(data))
    if (int(len(bin(data))/2) <30):                     #RFID data length is too small; Tampered RFID 
        return 0
    remainder = data // (2**int(len(bin(data))/2)-1)    #Cheking if the data in RFID is symmetrical; else Tampered RFID
    data = data >> int(len(bin(data))/2)
    if data == remainder:
        return 1                                        #Authentic RFID data
    else:
        return 0                                        #Tampered RFID

#Main function which handles all transmissions, reception and authentication other than STOP messages and Challenge response authntication of client and server
def main_tx_thread(sock,RTT):
    if(STOP == 1):              #if STOP messge is received from Server then terminate this function and train has to be stopped
        return
    data = rfid_read()          #Read RFID data
    if "AUTH" in data:          #used to handle exceptions in rfid read operations (if rfid is is not brought close enough to the reader)
        print("----------------------------------------------")
        return (0,0)                        #data is not valid
    if(check_data(data) != 1):              #Unauthorised rfid card detected as the data in the rfid card is not symmetrical
        print("Unauthorised rfid card")
        print("----------------------------------------------")
        return (0,0)                                     #data is not valid
    if data == None:
        print("None detected")                           #exception handling
        print("----------------------------------------------")
        return (0,0)                                     #data is not valid
    packet = decode_rfid_data(str(data),RTT)             #Decoded RFID data
    tx_packet = crc(str(packet))
    data_to_transmit = encrypt_message(str(tx_packet))   #Encrypted RFID data

    RTT = transmit(sock, data_to_transmit)
    if RTT == None:                                      #STOP signal received on TX - Port;  stopping train
        print("***************************************STOP STOP STOP***************************************")
    print("----------------------------------------------")
    print_packet(bin(packet))
    print("----------------------------------------------")
    return (RTT,1)                                       #return RTT with valid flag
    
#Thread for listening to STOP messages from server
def listen_for_STOP(sock):
    global STOP                 #defining a global variable
    STOP =0                     #intilizing global variable to 0; i.e  train running
    Client_IP = socket.gethostbyname(socket.gethostname())              #Get device IP address
    sock_stop = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)        #create a socket to listen for stop messages
    client_address = (Client_IP, (CLIENT_PORT+1))                       #STOP messages are received on the port after the one whihc is used to listen and transmit all main data       
    sock_stop.bind(client_address)                                      #bind stop port which is tx_port+1 to the ip
    print("Your Client-TX IP Address is: " + Client_IP)
    while True:                                 #infinite loop to continously check for stop messages
        print("listen for STOP started")
        data, server = sock_stop.recvfrom(4096)
        
        if STOP_MESSAGE == decrypt_message(data):           #received data is stop message
            print("***************************************STOP STOP STOP***************************************")
            print(f"TRAIN STOPPED:                : {TRAIN_NUMBER}")    
            # print(f'Other train is at a distance less than: {int(decrypt_message(data2))}')
            print("***************************************STOP STOP STOP***************************************")
            sock_stop.sendto(encrypt_message(str(ACK_MESSAGE_CLIENT)), (SERVER_IP, SERVER_PORT+4))      #repeatedly Sending acks for stop messages to server (server's main port is not used for this)
            time.sleep(0.78)
            sock_stop.sendto(encrypt_message(str(ACK_MESSAGE_CLIENT)), (SERVER_IP, SERVER_PORT+4))
            time.sleep(0.78)
            sock_stop.sendto(encrypt_message(str(ACK_MESSAGE_CLIENT)), (SERVER_IP, SERVER_PORT+4))
            time.sleep(0.78)
            sock_stop.sendto(encrypt_message(str(ACK_MESSAGE_CLIENT)), (SERVER_IP, SERVER_PORT+4))
            time.sleep(0.78)
            sock_stop.sendto(encrypt_message(str(ACK_MESSAGE_CLIENT)), (SERVER_IP, SERVER_PORT+4))
            STOP =1      #variable used to terminate all other functions
            break

#Function used to authenticate the server using challenge and rensponse
def auth_server(sock):
    server_address = (SERVER_IP, SERVER_PORT+1)     #main server port is not used for this
    while True:
        sock.sendto(encrypt_message(CHALLENGE_FROM_CLIENT), server_address) #encrypt and send challenge
        sock.settimeout(AUTH_TIMEOUT)
        try:
            data, address = sock.recvfrom(4096)
            data = decrypt_message(data)
        except socket.timeout:
            print("auth_client timeout")
            continue
        if data == RESPONSE_TO_CLIENT:              #received data is correct or not?
            print("SERVER authentication done")
            #SERVER authentication done
            status = auth_client(sock)
            if status ==1:
                break
    print("Everything authenticated")
    return

#Function used to authenticate client/train
def auth_client(sock):
    print("auth server called")
    server_address = (SERVER_IP, SERVER_PORT+1)         #main server port is not used for this
    print(sock)
    print (f'receiving challenge from server:{server_address}')
    data, address = sock.recvfrom(4096)
    print("received challenge from server")
    data = decrypt_message(data)
    if address == server_address:                       #checking if challenge received is from the right server and not from somewhere else
        print("address is server address")
        server_address = (SERVER_IP, SERVER_PORT+2)     #main server port is not used for sending the response
        print(f"sending response to server's challenge: {server_address}")
        sock.sendto(encrypt_message(RESPONSE_TO_SERVER), server_address)    #encrypt and send response
        print("CLIENT authentication done")
        #Client authentication done
        server_address = (SERVER_IP, SERVER_PORT+3)     #change server's port again to send in the first packet
        print("going into first_packet_tx")
        if(first_packet_tx(sock,RTT,server_address) == (None,0)):   #Transmittig the first packet
            return 0
        print("done into first_packet_tx")
        return 1
    return 0   

#Function used to transmit the first packet to the server after challenge response authentication is done
def transmit_first_packet(sock, data_to_transmit,server_address):
    # Send a message to the server
    packet_loss = 0
    for i in range(1,2):                #execute loop only once
        print("Sending...")
        start_ms = int(round(time.time() * 1000000))
        sock.sendto(data_to_transmit, server_address)

        # Wait for a response from the server
        sock.settimeout(TRANSMISSION_TIMEOUT)
        try:
            data, server = sock.recvfrom(4096)
        except socket.timeout:
            packet_loss += 1
            print("Server is not responding. Retransmitting data...")
            return None
        print("packet Loss: ",packet_loss)
        if ACK_MESSAGE_SERVER == decrypt_message(data):
            stop_ms = int(round(time.time() * 1000000))
            RTT = round((stop_ms-start_ms)/20)
            print(decrypt_message(data))
            print("RTT: ",(RTT*20))
            break


        print('ACK from server is incorrect, retransmitting the data')
    
    print('ACK received from {}:{}'.format(server[0], server[1]))
    print(decrypt_message(data))
    return (RTT)

#Function use to calculate the remaininder of division of large numbers; used in CRC
def mod_large_number(number, divisor):
    result = 0
    for bit in number:
        result = (result << 1 | int(bit)) % divisor
    return result

#function to extract first 8 bits from a binary string
def extract_first_8_bits(binary_string):
    return binary_string[-8:]

#function to remove first 8 bits from a binary string
def remove_first_8_bits(binary_string):
    return binary_string[:-8]

# function to verify if the received message's crc is correct
def verify_crc(data):
    crc_data = extract_first_8_bits(data)
    data = remove_first_8_bits(data)
    
    print("Check CRC started")
    data = int(data,2)
    remainder = mod_large_number(str(data), CRC_POLYNOMIAL)
    crc_ref = format(remainder, '08b')
    if(crc_data == crc_ref):        #if calculated CRC and received CRC is correct the return 1 else 0
        return 1
    else:
        return 0

#Function to calculate CRC
def crc(data):
    crc_data = mod_large_number(data, CRC_POLYNOMIAL)
    data = bin(int(data)) + format(crc_data, '08b')

    return data

#function to generate first packet to be transmitted after challenge response authentication
def first_packet_tx(sock,RTT, server_address):
    now = datetime.now()
    weekday = int(now.isoweekday())
    current_time = ((now.hour)*60*60 + (now.minute)*60 + (now.second))*weekday
    week_day            = weekday           #max 7
    train_no 		    = TRAIN_NUMBER      #max 65535
    station1 		    = 1                 #max 16383
    station2 	    	= 1                 #max 16383
    at_station_YN 		= 0                 #max 1
    reached_platform_YN = 0                 #max 1
    platform_ID 		= 0                 #max 31
    platform_entry_YN 	= 0                 #max 1
    branch_ID 		    = 0                 #max 63
    distance 		    = 0                 #max 63
    loop_line_YN 		= 0                 #max 1
    loop_line_ID 		= 0                 #max 1
    track_direction 	= 0                 #max 1
    tx_time 		    = current_time      #max 1048575
    speed 			    = 0                 #max 255
    stop 			    = 0                 #max 1
    direction 		    = 1                 #max 1
    latency 		    = 0                 #max 1023

    array		        = [week_day, train_no, station1, station2, at_station_YN, reached_platform_YN, platform_ID, platform_entry_YN, branch_ID, distance, loop_line_YN, loop_line_ID, track_direction, tx_time, speed, stop, direction, latency]
    size_array          = [3,16,14,14,1,1,5,1,6,6,1,1,1,20,8,1,1,10]
    string_array        = ""
    for i in range(0,18):
        string_array    = string_array + str(format(array[i], f"0{size_array[i]}b"))
    packet = int(string_array,2)

    tx_packet = crc(str(packet))
    data_to_transmit = encrypt_message(str(tx_packet))                 #Encrypted RFID data

    print(f'server address for first packet:{server_address}')

    RTT = transmit_first_packet(sock, data_to_transmit,server_address)
    if RTT == None:                                                 #check if the RTT is none or not
        print("Auth not completed... Retrying")                     
        return (None, 0)
    print("----------------------------------------------")
    print_packet(bin(packet))
    print("----------------------------------------------")
    return (RTT,1)   



print(f'Train Number     :{TRAIN_NUMBER}')
print(f'Train started on :{WEEKDAY_START_OF_TRAIN}')

Client_IP = socket.gethostbyname(socket.gethostname())  #getting the client/train ip to start udp communication
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_address = (Client_IP, CLIENT_PORT)
sock.bind(client_address)
print("Your Client-TX IP Address is: " + Client_IP)

threading.Thread(target=listen_for_STOP, args=(sock,)).start()  #creating parallel thread for listening to stop messages

RTT = 0
auth_server(sock)           #start the challenge response authentication
print("done authentication")
while True:
    (temp, is_RTT) = main_tx_thread(sock,RTT)   #start the main function to tx packets
    try:
        GPIO.cleanup()
    finally:
        GPIO.cleanup()
    if is_RTT == 1:             #Valid RTT is received
        RTT = temp
    if (STOP == 1):             #if train stop message is received from server then terminate the while loop
        break
print(f'STOP : {STOP}')
print("*****************************************")
sys.exit()                      #exit the program