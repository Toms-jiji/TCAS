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
ACK_MESSAGE_SERVER              = "ACK_from_server"
ACK_MESSAGE_CLIENT              = "ACK_from_client"
STOP_MESSAGE                    = "STOP STOP STOP"
SERVER_PORT                     = 10000  
CLIENT_PORT                     = 11000
PACKET_TX_RATE                  = 2
NUMBER_OF_TRAINS_TO_SIMULATE    = 1
RTT_SCALING_FACTOR              = 20
SERVER_IP                       = "10.217.68.205"
TRANSMISSION_TIMEOUT            = 2

WEEKDAY_START_OF_TRAIN          = 5
TRAIN_NUMBER                    = 1105
SPEED                           = 50

key = b'NaYMfYO0C8jy4fF1ImKOMobqqvq7FMlxDCIZDFIOShk='
global data_to_transmit
fernet = Fernet(key)

reader = SimpleMFRC522()
is_reading = True
GPIO.setwarnings(False)

class Train_node:
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
            self.weekday       	     = data_list[0] 			#3bits
            self.train_no        	 = data_list[1]			    #16bits
            
            self.station1         	 = data_list[2]			    #14bits
            self.station2  	      	 = data_list[3]			    #14bits
            self.at_station_YN     	 = data_list[4]		        #1bit
            self.reached_platform_YN = data_list[5]	            #1bit
            self.platform_ID 	     = data_list[6]			    #5bits
            self.platform_entry_YN	 = data_list[7]	            #1bit
            self.branch_ID	 	     = data_list[8]			    #6bits
            self.distance		     = data_list[9]			    #6bits
            self.loop_line_YN	     = data_list[10]			#1bit
            self.loop_line_ID	     = data_list[11]			#1bit
            self.track_direction	 = data_list[12]		    #1bit
            
            self.tx_time   		     = data_list[13]		    #20bits
            self.speed     		     = data_list[14]            #8bits		#Max is 200kmph and resolution is 1kmph
            self.stop      		     = data_list[15]			#1bit
            self.direction 		     = data_list[16]           	#1bit		# 0-> towards station 1      1-> towards station 2
            self.latency   		     = data_list[17]            #10bits		#Max is 2048ms and resolution is 2ms
            self.next		         = None
    def show(self):
        hour = round((self.tx_time/self.weekday)//(60*60))
        min = round(((self.tx_time/self.weekday)%(60*60))//(60))
        sec = round(((self.tx_time/self.weekday)%(60*60))%(60))

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
        
def encrypt_message(message):
    return fernet.encrypt(message.encode())

def decrypt_message(message):
    # Encode the message to bytes
    message_bytes = message

    # Decrypt the message
    decrypted_message = fernet.decrypt(message_bytes)

    # Return the decrypted message
    return decrypted_message.decode()

def int_to_binary(num, bits):
    return format(num, f"0{bits}b")

#function to print a packet
def print_packet(packet):
    size_array          = [3,16,14,14,1,1,5,1,6,6,1,1,1,20,8,1,1,10]
    packet = int(packet)
    array = [None]*18
    for i in range(0,18):
        array [17-i] = packet & ((2**(size_array[17-i]))-1)
        packet = packet >> (size_array[17-i])
    Train = Train_node(array)
    Train.show()
   
def check_number_in_list(number, list):
    if number in list:
        return True
    else:
        return False

def transmit(sock, data_to_transmit):
    # Send a message to the server
    packet_loss = 0
    while True:
        server_address = (SERVER_IP, SERVER_PORT)
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
            continue
        print("packet Loss: ",packet_loss)
        if ACK_MESSAGE_SERVER == decrypt_message(data):
            stop_ms = int(round(time.time() * 1000000))
            RTT = round((stop_ms-start_ms)/20)
            print(decrypt_message(data))
            print("RTT: ",(RTT*20))
            break
        elif STOP_MESSAGE == decrypt_message(data):
            return None

        print('ACK from server is incorrect, retransmitting the data')
    
    print('ACK received from {}:{}'.format(server[0], server[1]))
    print(decrypt_message(data))
    return (RTT)

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
    direction 		    = 0                                     #max 1
    latency 		    = RTT

    message = int(message)

    station1 		    = extract_bits(message, 14, 0)
    station2 	    	= extract_bits(message, 14, 14)
    if(station1 == station2):       #RFID card is at a station (not in parking space)
        at_station_YN 		= 1
        reached_platform_YN 	= extract_bits(message, 1, 28) 
        if (reached_platform_YN == 1):                               #RFID card is at a platform
            platform_ID 		= extract_bits(message, 5, 29)
            platform_entry_YN   = extract_bits(message, 1, 34)
        else:                                                       #RFID is not at a platform but a branch track at a station
            branch_ID 		    = extract_bits(message, 6,  29)
    else:
        distance 		    = extract_bits(message, 6,  28)
        loop_line_YN 		= extract_bits(message, 1,  34)
        loop_line_ID 		= extract_bits(message, 1,  35)
        track_direction 	= extract_bits(message, 1,  36)

    array		        = [week_day, train_no, station1, station2, at_station_YN, reached_platform_YN, platform_ID, platform_entry_YN, branch_ID, distance, loop_line_YN, loop_line_ID, track_direction, tx_time, speed, stop, direction, latency]
    size_array          = [3,16,14,14,1,1,5,1,6,6,1,1,1,20,8,1,1,10]
    string_array        = ""
    for i in range(0,18):
        string_array    = string_array + str(format(array[i], f"0{size_array[i]}b"))
    return int(string_array,2)

#function to check if data is valid
def check_data(data):
    try:
        data = int(str(data))
    except ValueError:
        return 0
    
    data = int(str(data))
    if (int(len(bin(data))/2) <30):
        return 0
    remainder = data // (2**int(len(bin(data))/2)-1)
    data = data >> int(len(bin(data))/2)
    if data == remainder:
        return 1
    else:
        return 0

def main_tx_thread(sock,RTT):
    data = rfid_read()
    if "AUTH" in data:
        print("----------------------------------------------")
        return (0,0)                                                #data is not valid
    if(check_data(data) != 1):
        print("Unauthorised rfid card")
        print("----------------------------------------------")
        return (0,0)                                                #data is not valid
    if data == None:
        print("None detecteed")
        print("----------------------------------------------")
        return (0,0)                                                #data is not valid
    packet = decode_rfid_data(str(data),RTT)                        #Decoded RFID data
    data_to_transmit = encrypt_message(str(packet))                 #Encrypted RFID data

    RTT = transmit(sock, data_to_transmit)
    if RTT == None:                                                 #STOP signal received on TX - Port;  stopping train
        print("***************************************STOP STOP STOP***************************************")
    print("----------------------------------------------")
    print_packet(packet)
    print("----------------------------------------------")
    return (RTT,1)                                                  #return RTT with valid flag
    

def listen_for_STOP(sock):
    Client_IP = socket.gethostbyname(socket.gethostname())              #Get device IP address
    sock_stop = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)        #create a socket to listen for stop messages
    client_address = (Client_IP, (CLIENT_PORT+1))                       
    sock_stop.bind(client_address)                                      #bind stop port which is tx_port+1 to the ip
    print("Your Client-TX IP Address is: " + Client_IP)
    while True:
        print("listen for STOP started")
        data, server = sock_stop.recvfrom(4096)
        # print(data)
        if STOP_MESSAGE == decrypt_message(data):
            print("***************************************STOP STOP STOP***************************************")
            print(f"TRAIN STOPPED:                : {TRAIN_NUMBER}")    
            print("***************************************STOP STOP STOP***************************************")
                

print(f'Train Number     :{TRAIN_NUMBER}')
print(f'Train started on :{WEEKDAY_START_OF_TRAIN}')

Client_IP = socket.gethostbyname(socket.gethostname())
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_address = (Client_IP, CLIENT_PORT)
sock.bind(client_address)
print("Your Client-TX IP Address is: " + Client_IP)

threading.Thread(target=listen_for_STOP, args=(sock,)).start() 

RTT = 0
while True:
    (temp, is_RTT) = main_tx_thread(sock,RTT)
    try:
        GPIO.cleanup()
    finally:
        GPIO.cleanup()
    if is_RTT == 1:             #Valid RTT is received
        RTT = temp
