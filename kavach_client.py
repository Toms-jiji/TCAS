import socket
import time
from datetime import datetime
import random
from cryptography.fernet import Fernet
from random import randint
import threading

##########################################################################
#Author: Toms Jiji Varghese
#Date: 15/11/2023
#Time: 12:06am
#Rev: 1.4
#GitHub: https://github.com/Toms-jiji/Kavach/tree/master
##########################################################################

ACK_MESSAGE_SERVER = "ACK_from_server"
ACK_MESSAGE_CLIENT = "ACK_from_client"
STOP_MESSAGE       = "STOP STOP STOP"
SERVER_PORT   =10000  
PACKET_TX_RATE = 2
NUMBER_OF_TRAINS_TO_SIMULATE = 1
RTT_SCALING_FACTOR  =   20
SERVER_IP = "127.0.0.1"
TRANSMISSION_TIMEOUT = 0.2

RANDOM_DATA = False                      #Generates packet using a random number generator                                                           
BETWEEN_SAME_STATION = False             #Generated packets with different station1 and station 2
TRAINS_AT_STATIONS = False               #Generated packets for trains which are currently at a station
TRAIN_AT_PARKING_LOT = False             #Generated packets for trains which are currently at a parking/storage space -->TRAIN_AT_PARKING_LOT_TRIGGER should be True
TRAIN_AT_PARKING_LOT_TRIGGER = False     #Trigger for parking lot condition.
ONE_TRAIN_IN_LOOP_LINE = False           #Generated packets such that one of the trains is in a loop line


FIXED_DISTANCE = False                   #True -> Braking is based on a predefine distance ; False -> Braking is based on the relative speed

HEAD_ON = True                          #Trains are going opposite to each other
TRAINS_GOING_AWAY = True                #Trains are going away

TAIL_END = False                        #Trail end collision condition    

MIN_BRACKING_DISTANCE_HEAD_ON_COLLISION   =   10 
MIN_BRACKING_DISTANCE_REAR_END_COLLISION  =   MIN_BRACKING_DISTANCE_HEAD_ON_COLLISION
MIN_DECELERATION        =   6480                #km/hr^2

if HEAD_ON == True:
    NUMBER_OF_TRAINS_TO_SIMULATE = 2

if TAIL_END == True:
    NUMBER_OF_TRAINS_TO_SIMULATE = 2

if TRAINS_AT_STATIONS == True:
    NUMBER_OF_TRAINS_TO_SIMULATE = 2

if ONE_TRAIN_IN_LOOP_LINE == True:
    NUMBER_OF_TRAINS_TO_SIMULATE = 2

key = b'NaYMfYO0C8jy4fF1ImKOMobqqvq7FMlxDCIZDFIOShk='

global data_to_transmit

fernet = Fernet(key)

# Create a Lock object
lock = threading.Lock()



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

def extract_bits(message, extract_bits, left_shift_by):
    return (message >> left_shift_by) & (2**(extract_bits)-1)

def print_packet(packet):
    size_array          = [3,16,14,14,1,1,5,1,6,6,1,1,1,20,8,1,1,10]
    packet = int(packet)
    array = [None]*18
    for i in range(0,18):
        array [17-i] = packet & ((2**(size_array[17-i]))-1)
        packet = packet >> (size_array[17-i])
    Train = Train_node(array)
    Train.show()

def create_packet(train_number, weekday, latency,speed):
    global BETWEEN_SAME_STATION
    global TRAINS_AT_STATIONS
    global ONE_TRAIN_IN_LOOP_LINE
    global FIXED_DISTANCE
    global HEAD_ON
    global TAIL_END


    now = datetime.now()
    current_time = ((now.hour)*60*60 + (now.minute)*60 + (now.second))*weekday
    week_day            = weekday           #max 7
    train_no 		    = train_number      #max 65535
    station1 		    = 9010              #max 16383
    station2 	    	= 9011              #max 16383
    at_station_YN 		= 0                 #max 1
    reached_platform_YN = 0                 #max 1
    platform_ID 		= 0                 #max 31
    platform_entry_YN 	= 0                 #max 1
    branch_ID 		    = 0                 #max 63
    distance 		    = 23                #max 63
    loop_line_YN 		= 0                 #max 1
    loop_line_ID 		= 0                 #max 1
    track_direction 	= 0                 #max 1
    tx_time 		    = current_time      #max 1048575
    if FIXED_DISTANCE == False:
        speed 			    = 10                #max 255
    else:
        speed 			    = speed
    stop 			    = 0                 #max 1
    direction 		    = 0                 #max 1
    latency 		    = latency               #max 1023

    if TRAINS_AT_STATIONS==True:
        print("at stations")
        now = datetime.now()
        current_time = ((now.hour)*60*60 + (now.minute)*60 + (now.second))*weekday
        week_day            = weekday                               #max 7
        train_no 		    = train_number                          #max 65535
        station1 		    = 9010                                  #max 16383
        station2 	    	= 9010                                  #max 16383
        at_station_YN 		= 1                                     #max 1
        reached_platform_YN = 0                                     #max 1
        platform_ID 		= 0                                     #max 31
        platform_entry_YN 	= 0                                     #max 1
        branch_ID 		    = 0                                     #max 63
        distance 		    = 0                                     #max 63
        loop_line_YN 		= 0                                     #max 1
        loop_line_ID 		= 0                                     #max 1
        track_direction 	= 0                                     #max 1
        tx_time 		    = current_time                          #max 1048575
        speed 			    = speed                                 #max 255
        stop 			    = 0                                     #max 1
        direction 		    = 0                                     #max 1
        latency 		    = latency                               #max 1023

    elif RANDOM_DATA==True:
        now = datetime.now()
        current_time = ((now.hour)*60*60 + (now.minute)*60 + (now.second))*weekday
        week_day            = weekday           #max 7
        train_no 		    = train_number      #max 65535
        station1 		    = 9010              #max 16383
        station2 	    	= random.randint(1000, 1020)              #max 16383
        at_station_YN 		= 0                 #max 1
        reached_platform_YN = 0                 #max 1
        platform_ID 		= 0                 #max 31
        platform_entry_YN 	= 0                 #max 1
        branch_ID 		    = 0                 #max 63
        distance 		    = random.randint(1,25)                #max 63
        loop_line_YN 		= 0                 #max 1
        loop_line_ID 		= 0                 #max 1
        track_direction 	= random.randint(0,1)                 #max 1
        tx_time 		    = current_time      #max 1048575
        speed 			    = speed                #max 255
        stop 			    = 0                 #max 1
        direction 		    = 0                 #max 1
        latency 		    = latency               #max 1023
    
    elif TRAIN_AT_PARKING_LOT==True:
        now = datetime.now()
        current_time = ((now.hour)*60*60 + (now.minute)*60 + (now.second))*weekday
        week_day            = weekday                               #max 7
        train_no 		    = train_number                          #max 65535
        station1 		    = 9010                                  #max 16383
        station2 	    	= 0                                  #max 16383
        at_station_YN 		= 1                                     #max 1
        reached_platform_YN = 0                                     #max 1
        platform_ID 		= 0                                     #max 31
        platform_entry_YN 	= 0                                     #max 1
        branch_ID 		    = 0                                     #max 63
        distance 		    = 0                                     #max 63
        loop_line_YN 		= 0                                     #max 1
        loop_line_ID 		= 0                                     #max 1
        track_direction 	= 0                                     #max 1
        tx_time 		    = current_time                          #max 1048575
        speed 			    = speed                                 #max 255
        stop 			    = 0                                     #max 1
        direction 		    = 0                                     #max 1
        latency 		    = latency                               #max 1023

    elif ONE_TRAIN_IN_LOOP_LINE==True:
        now = datetime.now()
        current_time = ((now.hour)*60*60 + (now.minute)*60 + (now.second))*weekday
        week_day            = weekday                               #max 7
        train_no 		    = train_number                          #max 65535
        station1 		    = 9010                                  #max 16383
        station2 	    	= 9011                                  #max 16383
        at_station_YN 		= 0                                     #max 1
        reached_platform_YN = 0                                     #max 1
        platform_ID 		= 0                                     #max 31
        platform_entry_YN 	= 0                                     #max 1
        branch_ID 		    = 0                                     #max 63
        distance 		    = 23                                    #max 63
        loop_line_YN 		= 1                                     #max 1  -- first loopline after the rfid with distance 23
        loop_line_ID 		= 0                                     #max 1  -- Not required
        track_direction 	= 0                                     #max 1
        tx_time 		    = current_time                          #max 1048575
        speed 			    = speed                                 #max 255
        stop 			    = 0                                     #max 1
        direction 		    = 0                                     #max 1
        latency 		    = latency                               #max 1023

    if FIXED_DISTANCE == True:
        if HEAD_ON==True and TRAINS_GOING_AWAY==True:
            now = datetime.now()
            current_time = ((now.hour)*60*60 + (now.minute)*60 + (now.second))*weekday
            week_day            = weekday                               #max 7
            train_no 		    = train_number                          #max 65535
            station1 		    = 9010                                  #max 16383
            station2 	    	= 9011                                  #max 16383
            at_station_YN 		= 0                                     #max 1
            reached_platform_YN = 0                                     #max 1
            platform_ID 		= 0                                     #max 31
            platform_entry_YN 	= 0                                     #max 1
            branch_ID 		    = 0                                     #max 63
            distance 		    = 23+MIN_BRACKING_DISTANCE_HEAD_ON_COLLISION+1                                    #max 63
            loop_line_YN 		= 0                                     #max 1  -- first loopline after the rfid with distance 23
            loop_line_ID 		= 0                                     #max 1  -- Not required
            track_direction 	= 0                                     #max 1
            tx_time 		    = current_time                          #max 1048575
            speed 			    = speed                                 #max 255
            stop 			    = 0                                     #max 1
            direction 		    = 1                                     #max 1
            latency 		    = latency                               #max 1023

        elif HEAD_ON==True and TRAINS_GOING_AWAY==False:
            now = datetime.now()
            current_time = ((now.hour)*60*60 + (now.minute)*60 + (now.second))*weekday
            week_day            = weekday                               #max 7
            train_no 		    = train_number                          #max 65535
            station1 		    = 9010                                  #max 16383
            station2 	    	= 9011                                  #max 16383
            at_station_YN 		= 0                                     #max 1
            reached_platform_YN = 0                                     #max 1
            platform_ID 		= 0                                     #max 31
            platform_entry_YN 	= 0                                     #max 1
            branch_ID 		    = 0                                     #max 63
            distance 		    = 23-MIN_BRACKING_DISTANCE_HEAD_ON_COLLISION+1                                    #max 63
            loop_line_YN 		= 0                                     #max 1  -- first loopline after the rfid with distance 23
            loop_line_ID 		= 0                                     #max 1  -- Not required
            track_direction 	= 0                                     #max 1
            tx_time 		    = current_time                          #max 1048575
            speed 			    = speed                                 #max 255
            stop 			    = 0                                     #max 1
            direction 		    = 1                                     #max 1
            latency 		    = latency                               #max 1023

        elif TAIL_END==True:
            now = datetime.now()
            current_time = ((now.hour)*60*60 + (now.minute)*60 + (now.second))*weekday
            week_day            = weekday                               #max 7
            train_no 		    = train_number                          #max 65535
            station1 		    = 9010                                  #max 16383
            station2 	    	= 9011                                  #max 16383
            at_station_YN 		= 0                                     #max 1
            reached_platform_YN = 0                                     #max 1
            platform_ID 		= 0                                     #max 31
            platform_entry_YN 	= 0                                     #max 1
            branch_ID 		    = 0                                     #max 63
            distance 		    = 23-MIN_BRACKING_DISTANCE_REAR_END_COLLISION+1                                    #max 63
            loop_line_YN 		= 0                                     #max 1  -- first loopline after the rfid with distance 23
            loop_line_ID 		= 0                                     #max 1  -- Not required
            track_direction 	= 0                                     #max 1
            tx_time 		    = current_time                          #max 1048575
            speed 			    = speed                                 #max 255
            stop 			    = 0                                     #max 1
            direction 		    = 0                                     #max 1
            latency 		    = latency                               #max 1023

    if FIXED_DISTANCE == False:
        if HEAD_ON==True and TRAINS_GOING_AWAY==True:
            now = datetime.now()
            current_time = ((now.hour)*60*60 + (now.minute)*60 + (now.second))*weekday
            week_day            = weekday                               #max 7
            train_no 		    = train_number                          #max 65535
            station1 		    = 9010                                  #max 16383
            station2 	    	= 9011                                  #max 16383
            at_station_YN 		= 0                                     #max 1
            reached_platform_YN = 0                                     #max 1
            platform_ID 		= 0                                     #max 31
            platform_entry_YN 	= 0                                     #max 1
            branch_ID 		    = 0                                     #max 63
            distance 		    = 24                                    #max 63
            loop_line_YN 		= 0                                     #max 1  -- first loopline after the rfid with distance 23
            loop_line_ID 		= 0                                     #max 1  -- Not required
            track_direction 	= 0                                     #max 1
            tx_time 		    = current_time                          #max 1048575
            speed 			    = 150                                   #max 255
            stop 			    = 0                                     #max 1
            direction 		    = 1                                     #max 1
            latency 		    = latency                               #max 1023

        elif HEAD_ON==True and TRAINS_GOING_AWAY==False:
            HEAD_ON = False
            now = datetime.now()
            current_time = ((now.hour)*60*60 + (now.minute)*60 + (now.second))*weekday
            week_day            = weekday                               #max 7
            train_no 		    = train_number                          #max 65535
            station1 		    = 9010                                  #max 16383
            station2 	    	= 9011                                  #max 16383
            at_station_YN 		= 0                                     #max 1
            reached_platform_YN = 0                                     #max 1
            platform_ID 		= 0                                     #max 31
            platform_entry_YN 	= 0                                     #max 1
            branch_ID 		    = 0                                     #max 63
            distance 		    = 21                                   #max 63
            loop_line_YN 		= 0                                     #max 1  -- first loopline after the rfid with distance 23
            loop_line_ID 		= 0                                     #max 1  -- Not required
            track_direction 	= 0                                     #max 1
            tx_time 		    = current_time                          #max 1048575
            speed 			    = 150                                   #max 255
            stop 			    = 0                                     #max 1
            direction 		    = 1                                     #max 1
            latency 		    = latency                               #max 1023

        elif TAIL_END==True:
            now = datetime.now()
            current_time = ((now.hour)*60*60 + (now.minute)*60 + (now.second))*weekday
            week_day            = weekday                               #max 7
            train_no 		    = train_number                          #max 65535
            station1 		    = 9010                                  #max 16383
            station2 	    	= 9011                                  #max 16383
            at_station_YN 		= 0                                     #max 1
            reached_platform_YN = 0                                     #max 1
            platform_ID 		= 0                                     #max 31
            platform_entry_YN 	= 0                                     #max 1
            branch_ID 		    = 0                                     #max 63
            distance 		    = 24                                    #max 63
            loop_line_YN 		= 0                                     #max 1  -- first loopline after the rfid with distance 23
            loop_line_ID 		= 0                                     #max 1  -- Not required
            track_direction 	= 0                                     #max 1
            tx_time 		    = current_time                          #max 1048575
            speed 			    = 150                                   #max 255
            stop 			    = 0                                     #max 1
            direction 		    = 0                                     #max 1
            latency 		    = latency                               #max 1023
    
    if BETWEEN_SAME_STATION == False:
        station2 	    	= random.randint(1500, 2000)
        station2 	    	= random.randint(1000, 1500)  

    size_array          = [3,16,14,14,1,1,5,1,6,6,1,1,1,20,8,1,1,10]
    array		        = [week_day, train_no, station1, station2, at_station_YN, reached_platform_YN, platform_ID, platform_entry_YN, branch_ID, distance, loop_line_YN, loop_line_ID, track_direction, tx_time, speed, stop, direction, latency]
    string_array        = ""
    
    print("current_time:")
    print(current_time)
    for i in range(0,18):
        string_array    = string_array + format(array[i], f"0{size_array[i]}b")
    return int(string_array,2)
    
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

def print_all_def():
    print(f"BETWEEN_SAME_STATION                    : {BETWEEN_SAME_STATION}")
    print(f"TRAINS_AT_STATIONS                      : {TRAINS_AT_STATIONS}")
    print(f"TRAIN_AT_PARKING_LOT                    : {TRAIN_AT_PARKING_LOT}")
    print(f"TRAIN_AT_PARKING_LOT_TRIGGER            : {TRAIN_AT_PARKING_LOT_TRIGGER}")
    print(f"ONE_TRAIN_IN_LOOP_LINE                     : {ONE_TRAIN_IN_LOOP_LINE}")
    print(f"FIXED_DISTANCE                          : {FIXED_DISTANCE}")
    print(f"HEAD_ON                                 : {HEAD_ON}")
    print(f"TAIL_END                                : {TAIL_END}")
    

def train_instance(train_number):
    global BETWEEN_SAME_STATION
    global TRAINS_AT_STATIONS
    global ONE_TRAIN_IN_LOOP_LINE
    global FIXED_DISTANCE
    global HEAD_ON
    global TAIL_END


    weekday = randint(1,7)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    RTT = 0
    speed = random.randint(1,100)
    while True:  
        if ONE_TRAIN_IN_LOOP_LINE == True:
            ONE_TRAIN_IN_LOOP_LINE
            packet = create_packet(train_number, weekday, RTT, speed)
            ONE_TRAIN_IN_LOOP_LINE = False

        elif HEAD_ON == True:
            packet = create_packet(train_number, weekday, RTT, speed)
            HEAD_ON = False

        elif TAIL_END == True:
            packet = create_packet(train_number, weekday, RTT, speed)
            TAIL_END = False

        elif TRAIN_AT_PARKING_LOT_TRIGGER == True:
            TRAINS_AT_STATIONS
            TRAIN_AT_PARKING_LOT
            if TRAIN_AT_PARKING_LOT !=True:
                TRAINS_AT_STATIONS = True
            packet = create_packet(train_number, weekday, RTT, speed)
            TRAINS_AT_STATIONS = False
            TRAIN_AT_PARKING_LOT = True

        else:
            packet = create_packet(train_number, weekday, RTT, speed)

        lock.acquire()
        print("----------------------------------------------")
        data_to_transmit = encrypt_message(str(packet))
        RTT = transmit(sock, data_to_transmit)
        if RTT == None:
            print("***************************************STOP STOP STOP***************************************")
        print_packet(packet)
        print("----------------------------------------------")
        lock.release()
        sock.settimeout(PACKET_TX_RATE)
        try:
            data, server = sock.recvfrom(4096)
            if STOP_MESSAGE == decrypt_message(data):
                print("***************************************STOP STOP STOP***************************************")
                print("***************************************STOP STOP STOP***************************************")
                print(f"TRAIN STOPPED:                : {train_number}")
            return
        except:
            continue

        


train_numbers = []
for i in range(NUMBER_OF_TRAINS_TO_SIMULATE):
    random_number = randint(1000, 2000)
    while check_number_in_list(random_number, train_numbers)==True:
       random_number = randint(1000, 2000)
    train_numbers.append(random_number)
    i=i+1
print("Trains are:")
print(train_numbers)

for i in range(0,NUMBER_OF_TRAINS_TO_SIMULATE):
    threading.Thread(target=train_instance, args=(train_numbers[i],)).start() 
