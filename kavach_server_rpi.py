import socket
import threading
from cryptography.fernet import Fernet
from datetime import datetime
import threading
import time

################################################################################################
#   Author: Toms Jiji Varghese                                                                 #
#   Date: 19/11/2023                                                                           #
#   Time: 11:55pm                                                                              #
#   Rev: 1.7                                                                                   #
#   GitHub: https://github.com/Toms-jiji/Kavach/tree/master                                    #
#                                                                                              #
#   Copyright (c) 2023 toms jiji varghese. ALL RIGHTS RESERVED.                                #
#   This code is the sole property of Toms Jiji Varghese and may not be copied, distributed,   #
#   or modified without the express written permission of Toms Jiji Varghese.                  #
################################################################################################ 


FIXED_BRAKING_DISTANCE = True
ENABLE_STALE_PACKET_SCAN = False




BREAKING_DISTANCE  = 100
ACK_MESSAGE_SERVER = "ACK_from_server"
ACK_MESSAGE_CLIENT = "ACK_from_client"
CHALLENGE_FROM_CLIENT = "What is your professor's name"
RESPONSE_TO_CLIENT    = "TVP"
CHALLENGE_FROM_SERVER = "What is your course name"
RESPONSE_TO_SERVER    = "TCP/IP"
AUTH_TIMEOUT           = 1
STALE_PACKET_TIMEOUT      = 15
ACK_TIMEOUT         = 1
CRC_POLYNOMIAL      = 198 #max 8bit
SERVER_IP          = "10.114.240.35"
RTT_SCALING        = 20
SERVER_PORT        = 10000
MIN_BRACKING_DISTANCE_HEAD_ON_COLLISION   =   10 
MIN_BRACKING_DISTANCE_REAR_END_COLLISION  =   MIN_BRACKING_DISTANCE_HEAD_ON_COLLISION
MIN_DECELERATION        =   6480                #km/hr^2


STOP_MESSAGE       = "STOP STOP STOP"
key                = b'NaYMfYO0C8jy4fF1ImKOMobqqvq7FMlxDCIZDFIOShk='       #encription key

print("Encryption Key: ",key)                               #printing encryption key
fernet = Fernet(key)                                        #passing the encryption key to the cryptography function

# Create a Lock object
lock = threading.Lock()

Train_head                = None        #head pointer for Train linkedlist
Database_of_stations_head = None        #head pointer for database of station's linkedlist

Train_LL_length                = 0        #Length of Train's linkedlist
Database_of_stations_LL_lenth  = 0        #Length of  database of station's linkedlist

# Class to store all train information
class Train_node:
    def __init__(self, data_list=None, time=None, train_ip=None, train_port=None):   #Total = 127bits
        if data_list is None:
            self.rcvd_time       	 = None
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
            self.train_ip   		 = None
            self.train_port   		 = None
            self.next		         = None
        
        elif time is None:
            self.rcvd_time       	 = None
            self.weekday       	     = data_list[0] 			#20bits
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
            self.train_ip   		 = train_ip
            self.train_port   		 = train_port
            self.next		         = None

        else:
            self.rcvd_time       	 = time
            self.weekday       	     = data_list[0] 			#20bits
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
            self.train_ip   		 = train_ip
            self.train_port   		 = train_port
            self.next		         = None

    def show(self):
        now = datetime.now()
        weekday = int(now.isoweekday())
        hour = round((self.tx_time/weekday)//(60*60))
        min = round(((self.tx_time/weekday)%(60*60))//(60))
        sec = round(((self.tx_time/weekday)%(60*60))%(60))
        print("Train details are:")
        print("rcvd_time 	    	:",self.rcvd_time)
        print("weekday   	    	:",self.weekday)
        print("train_no  	    	:",self.train_no)
        
        print("station1  	    	:",self.station1)
        print("station2  	    	:",self.station2)
        print("at_station_YN  		:",self.at_station_YN)
        print("reached_platform_YN      :",self.reached_platform_YN)
        print("platform_ID  		:",self.platform_ID)
        print("platform_entry_YN  	:",self.platform_entry_YN)
        print("branch_ID    		:",self.branch_ID)
        print("distance  	    	:",self.distance)
        print("loop_line_YN  		:",self.loop_line_YN)
        print("loop_line_ID  		:",self.loop_line_ID)
        print("track_direction  	:",self.track_direction)
        print(f"tx_time                 : {hour}:{min}:{sec}")
        print("speed     	    	:",self.speed)
        print("stop      	    	:",self.stop)
        print("direction 	    	:",self.direction)
        print("RTT (us)    	    	:",self.latency)
        print("Train IP   	    	:",self.train_ip)
        print("Train Port  	    	:",self.train_port)
        print("next   	    	        :",self.next)

#Class that created the linkedlist for trains and defines the funtions to process the train data
class Train_linked_list:
    def __init__(self):
        self.head = Train_node()                    #Node containing pointer to the first link

    def append(self,data_list, time, train_ip,train_port):
        new_node = Train_node(data_list, time,train_ip, train_port)      #Create a new node with the new data
        cur = self.head                             
        while cur.next != None:
            cur = cur.next
        cur.next = new_node                         #Swap the pointers

    #Function to insert data at an index in the linkedlist
    def arbitary_insert(self,index,data_list):      
        i=0
        new_node = Train_node(data_list)
        cur = self.head
        while cur.next:
            if i==index:
                break
            i+=1
            cur = cur.next
        new_node.next = cur.next
        cur.next = new_node

    #Function that identifies trains on the same track within alert distance
    def trains_on_same_track(self,my_train):
        head_on_collision = 0
        i=0
        cur = self.head
        trains_with_risk_of_collision = []      #Array containing trains with the risk of collision with the current train
        cur = cur.next
        while cur:
            if((cur.train_no==my_train.train_no)):
                cur = cur.next
                continue
            if ((my_train.station1 == 1)and(my_train.station2 == 1)):
                return
            if(cur.train_no==None):
                cur = cur.next
                continue
            if ((cur.station1==my_train.station1)and(cur.station2==my_train.station2)):        #Both trains are in the same set of tracks between two stations
                print("#Both trains are in the same set of tracks between two stations")
                if((my_train.station1!=my_train.station2)and(cur.station1!=cur.station2)):     #Both trains are not at a station
                    print("#Both trains are not at a station")
                    if(cur.track_direction==my_train.track_direction):                       #Both trains are in the same track UP/DOWM
                        print("#Both trains are in the same track UP/DOWN")
                        if((cur.loop_line_YN==my_train.loop_line_YN)):                       #Both trains are in the same loop line or main line
                            print("#Both trains are in the same loop line or main line")
                            # print(f"cur.speed:mytrain.speed    : {cur.speed}:{my_train.speed}:{(cur.speed!=0 and my_train.speed!=0)}")
                            
                            if((cur.speed!=0 and my_train.speed!=0)):                          #Both trains are not stopped
                                print("#Both trains are running")
                                if((cur.train_no!=my_train.train_no)):                       #Just verifying if the trains are not the same
                                    
                                    #Conditions for FIXED braking distance
                                    if FIXED_BRAKING_DISTANCE:   
                                        print("FIXED BRAKING DISTANCE SELECTED")                            
                                        if(cur.direction != my_train.direction):                                                            #Both trains are coming head on
                                            print("trains are going in the opposite direction")
                                            if(((cur.distance > my_train.distance)and(cur.direction == 0)) | ((my_train.distance>cur.distance)and(my_train.direction ==0))):    #Making sure that both trains are not going away from each other
                                                print("both trains are coming towards each other")
                                                if(abs(cur.distance - my_train.distance)<MIN_BRACKING_DISTANCE_HEAD_ON_COLLISION):              #Trains are too close
                                                    trains_with_risk_of_collision.append(cur.train_no)  
                                                    print("RISK OF COLLISION DETECTED...!!!")
                                                    head_on_collision = 1
                                                else:
                                                    print("#Distance betweent he trains is larger than then minimum breaking distance")
                                            else:
                                                print("#Both trains are going away from each other")
                                        else:
                                            print("trains are going in the same direction")
                                            if(abs(cur.distance - my_train.distance)<MIN_BRACKING_DISTANCE_REAR_END_COLLISION):             #Condition for rear end collision risk    
                                                print("trains are going in the same direction and within collision distance")
                                                head_on_collision = 0
                                                if(cur.direction==0):                                                                       #Both trains are going towards station 1 
                                                    print("both trains are going towards station1")
                                                    if(cur.distance > my_train.distance):                                                   #Cur train is the back one
                                                        print(f"Train number : {cur.train_no} is the back train")
                                                        trains_with_risk_of_collision.append(cur.train_no)                                  #STOP the back train
                                                    else:                                                                                   #my_train is the back one
                                                        print(f"Train number : {my_train.train_no} is the back train")
                                                        trains_with_risk_of_collision.append(my_train.train_no)                             #STOP my train
                                                    print("RISK OF COLLISION DETECTED...!!!")
                                                else:
                                                    print("both trains are going in towards station2")
                                                    if(cur.distance > my_train.distance):                                                   #my_train is the back one
                                                        print(f"Train number : {my_train.train_no} is the back train")
                                                        trains_with_risk_of_collision.append(my_train.train_no)                             #STOP my train
                                                    else:                                                                                   #Cur train is the back one
                                                        print(f"Train number : {cur.train_no} is the back train")
                                                        trains_with_risk_of_collision.append(cur.train_no)                                  #STOP cur train
                                                    print("RISK OF COLLISION DETECTED...!!!")
                                            else:
                                                print("#Trains are going in the same direction but are NOT within minimum braking distance for rear end collision")   

                                    #Conditions for VARIABLE braking distance
                                    else:
                                        print("VARIABLE BRAKING DISTANCE SELECTED -->> BASED ON RELATIVE SPEED OF TRAINS")
                                        if(cur.direction != my_train.direction):                                             #Both trains are coming for head on collision
                                            print("trains are going in the opposite direction")
                                            if(((cur.distance > my_train.distance)and(cur.direction == 0)) | ((my_train.distance>cur.distance)and(my_train.direction ==0))):    #Making sure that both trains are not going away from each other
                                                print("both trains are coming towards each other")
                                                del_speed_square =  (cur.speed + my_train.speed)**2
                                                bracking_distance =  del_speed_square/(2*MIN_DECELERATION)
                                                bracking_distance = bracking_distance*2
                                                print(f"Braking distance according to relative speed : {bracking_distance}")
                                                if(abs(cur.distance - my_train.distance)<(bracking_distance)):    
                                                    trains_with_risk_of_collision.append(cur.train_no)
                                                    print("RISK OF COLLISION DETECTED...!!!")
                                                    head_on_collision = 1
                                                else:
                                                    print("#Distance betweent he trains is larger than then minimum breaking distance based on their relative speed")
                                            else:
                                                print("#Both trains are going away from each other")
                                        else:
                                            print("trains are going in the same direction")
                                            del_speed_square =  (cur.speed - my_train.speed)**2
                                            bracking_distance =  del_speed_square/(2*MIN_DECELERATION)
                                            bracking_distance = bracking_distance*2
                                            print(f"Braking distance according to relative speed : {bracking_distance}")
                                            if(abs(cur.distance - my_train.distance)<bracking_distance):             #Condition for rear end collision risk    
                                                head_on_collision = 0
                                                print("trains are going in the same direction and within collision distance")
                                                if(cur.direction==0):                                                                       #Both trains are going towards station 1 
                                                    print("both trains are going towards station1")
                                                    if(cur.distance > my_train.distance):                                                   #Cur train is the back one
                                                        print(f"Train number : {my_train.train_no} is the back train")
                                                        trains_with_risk_of_collision.append(cur.train_no)                                  #STOP the back train
                                                    else:                                                                                   #my_train is the back one
                                                        print(f"Train number : {cur.train_no} is the back train")
                                                        trains_with_risk_of_collision.append(my_train.train_no)                             #STOP my train
                                                    print("RISK OF COLLISION DETECTED...!!!")
                                                else:
                                                    print("both trains are going towards station2")
                                                    if(cur.distance > my_train.distance):                                                   #my_train is the back one
                                                        print(f"Train number : {cur.train_no} is the back train")
                                                        trains_with_risk_of_collision.append(my_train.train_no)                             #STOP my train
                                                    else:                                                                                   #Cur train is the back one
                                                        print(f"Train number : {my_train.train_no} is the back train")
                                                        trains_with_risk_of_collision.append(cur.train_no)                                  #STOP cur train
                                                    print("RISK OF COLLISION DETECTED...!!!")
                                            else:
                                                print("#Trains are going in the same direction but are NOT within minimum braking distance wrt to relative speed for rear end collision")   
                                else:
                                    print("#Both trains have the same train number")
                            else:
                                print("#Both trains are stopped")
                        else:
                            print("#Both trains are NOT in the same loop line or main line")
                    else:
                        print("#Both trains are NOT in the same track UP/DOWN")
                else:
                    print("#Either one of the trains is at a station")                               
            else:
                print("#Both trains are NOT in the same set of tracks between two stations")                                       
                i+=1
            cur = cur.next
        if(trains_with_risk_of_collision):
            print("trains with high risk found")
            if(head_on_collision==1):
                print("head on collision... so appended my train")
                trains_with_risk_of_collision.append(my_train.train_no)
            print("Trains with risk of collision are: ", trains_with_risk_of_collision)
            for i in range (0, len(trains_with_risk_of_collision)):
                risky_trains = trains_with_risk_of_collision[i]
            return trains_with_risk_of_collision

    #Function to flush out / delete a train from the database. Used when the train reaches its destination
    def delete(self,train_no):
        cur = self.head
        while cur:
            if cur.train_no==train_no:
                prev.next = cur.next
                del cur
                break
            prev = cur
            cur = cur.next

    #Function to find a train from the linked list
    def find(self,train_no):
        i=0
        cur = self.head
        while cur.next:
            if cur.train_no==train_no:
                break
            i+=1
            cur = cur.next
        if cur.train_no==train_no:
            return (i-1,cur.tx_time)
        else:
            return (None,None)

    #Function to find a train from the linked list
    def find_other_trains_for_risk_with_stale_packet_trains(self,train_no):
        i=0
        cur = self.head
        station1=0
        station2=0
        Other_trains = []
        while cur.next:
            if cur.train_no==train_no:
                break
            i+=1
            cur = cur.next
        if cur.train_no==train_no:
            station1 = cur.station1
            station2 = cur.station2
            cur = self.head
            while True:
                if cur.station1==station1:
                    if cur.station2==station2:
                        Other_trains.append(cur.train_no)
                if cur.next == None:
                    break
                cur = cur.next
            return Other_trains
        else:
            return None

    #Function to find a train IP from the linked list    
    def find_train_IP_and_port(self,train_no):
        i=0
        cur = self.head
        cur = cur.next
        if cur.train_no==train_no:
            train_network_details = (cur.train_ip, cur.train_port)
            return train_network_details
            
        while cur:
            if cur.train_no==train_no:
                train_network_details = (cur.train_ip, cur.train_port)
                return train_network_details
            if cur.next == None:
                return None
            cur = cur.next

    #Function to update the details of a train which is already stored in the database   
    def update(self, data_list, time, train_ip, train_port):
        i=0
        cur = self.head
        new_node = Train_node(data_list, time, train_ip, train_port)
        prev = cur
        while cur.next:
            if cur.train_no==new_node.train_no:
                break
            i+=1
            prev = cur
            cur = cur.next
        if cur.train_no==new_node.train_no:
            prev.next = new_node
            new_node.next = cur.next
            del cur
        else:
            print("Train does not exit so data not updated")
            
    #Function to print all the details of a particular train
    def show(self,train_no):
        i=0
        cur = self.head
        while cur.next:
            if cur.train_no==train_no:
                break
            i+=1
            cur = cur.next
        if cur.train_no==train_no:
            cur.show()
        else:
            print("Train not found..!!!")

    #Function to calculate the lenght of the linked list. i.e number of running trains
    def length(self):
        cur = self.head
        total = 0
        while cur.next != None:
            total += 1
            cur = cur.next
        return total
    
    #Function to print the trains numbers of currently running trains
    def display(self):
        elems = []
        cur_node = self.head
        while cur_node.next!=None:
            cur_node = cur_node.next
            elems.append(cur_node.train_no)
        print (elems)

    #Function to get list of running trains
    def running_trains(self):
        train_no = []
        train_time = []
        cur_node = self.head
        while cur_node.next!=None:
            cur_node = cur_node.next
            train_no.append(cur_node.train_no)
            train_time.append(cur_node.tx_time)
        return (train_no, train_time)

    #Function to fetch train data from the database using the index of the linkedlist
    def get(self,index):
        cur_idx=0
        cur_node=self.head
        while True:
            cur_node=cur_node.next
            if cur_idx==index: 
                return cur_node.train_no
            if cur_node.next == None: 
                print ("ERROR: 'Get' Index out of range!") 
                return None
            cur_idx+=1

#Class for Binary search of the database. Future improvement         
class Database_of_stations:
    def __init__(self, station_no, station_ptr, next):
        self.station_no       	 = station_no
        self.station_ptr	 = station_ptr
        self.next		 = next
       
    def show(self):
        print("Train details are:")
        print("station_no 	    	:",self.station_no)
        print("station_ptr 	    	:",self.station_ptr)
        print("next 	    		:",self.next)

#Function to extract particular bits from the message
def extract_bits(message, extract_bits, left_shift_by):
#    print(bin((message >> left_shift_by) and (2**(extract_bits)-1)))
    return (message >> left_shift_by) & (2**(extract_bits)-1)

#Funcito the extract meaningful data from the bits received. It returns the data in an array
def extract_data(message):
    message = int(message, 2)
    weekday 		    = extract_bits(message, 3, 107)
    train_no 		    = extract_bits(message, 16, 91)
    station1 		    = extract_bits(message, 14, 77)
    station2 	    	= extract_bits(message, 14, 63)
    at_station_YN 		= extract_bits(message, 1,  62)
    reached_platform_YN = extract_bits(message, 1,  61)
    platform_ID 		= extract_bits(message, 5,  56)
    platform_entry_YN 	= extract_bits(message, 1,  55)
    branch_ID 		    = extract_bits(message, 6,  49)
    distance 		    = extract_bits(message, 6,  43)
    loop_line_YN 		= extract_bits(message, 1,  42)
    loop_line_ID 		= extract_bits(message, 1,  41)
    track_direction 	= extract_bits(message, 1,  40)
    tx_time 		    = extract_bits(message, 20, 20)
    speed 			    = extract_bits(message, 8,  12)
    stop 			    = extract_bits(message, 1,  11)
    direction 		    = extract_bits(message, 1,  10)
    latency 		    = extract_bits(message, 10, 0 )*RTT_SCALING
    array		        = [weekday, train_no, station1, station2, at_station_YN, reached_platform_YN, platform_ID, platform_entry_YN, branch_ID, distance, loop_line_YN, loop_line_ID, track_direction, tx_time, speed, stop, direction, latency]
    return array


#Function to encrypt the message
def encrypt_message(message):
    return fernet.encrypt(message.encode())

#Function to decrypt the message
def decrypt_message(message):
    # Decode the message to a string
    message_string = message.decode()

    # Decrypt the message
    decrypted_message = fernet.decrypt(message_string.encode())

    # Return the decrypted message
    return decrypted_message.decode()

def extract_first_8_bits(binary_string):
    return binary_string[-8:]

def remove_first_8_bits(binary_string):
    return binary_string[:-8]

def mod_large_number(number, divisor):
    result = 0
    for bit in number:
        result = (result << 1 | int(bit)) % divisor
    return result

def verify_crc(data):
    crc_data = extract_first_8_bits(data)
    data = remove_first_8_bits(data)
    data = int(data,2)
    remainder = mod_large_number(str(data), CRC_POLYNOMIAL)
    crc_ref = format(remainder, '08b')
    if(crc_data == crc_ref):
        return 1
    else:
        return 0

def crc(data):
    crc_data = mod_large_number(data, CRC_POLYNOMIAL)
    data = bin(int(data)) + format(crc_data, '08b')

    return data


#Function that each client thread will run
def handle_client(data, sock, address, first_Call, sock_for_acks):
    
    # Print the message and the client's address
    rcvd_message = decrypt_message(data)
    if(verify_crc(bin(int(rcvd_message,2)))!=1):
        print("CRC failed so discarding packet")
        return
    print("CRC passed")

    rcvd_message = remove_first_8_bits(bin(int(rcvd_message,2)))
    # Send a response back to the client
    tx_message = encrypt_message(ACK_MESSAGE_SERVER)
    sock.sendto(tx_message, address)

    lock.acquire()
    print("------------------------------------------------------------")
    print('Received {} bytes({}bits) from {}:{}'.format(len(rcvd_message),8*len(rcvd_message), address[0], address[1]))
    # print('Received Data: {}'.format(rcvd_message))


    print("ACK Sent")

    store_and_process_received_data(rcvd_message, address[0], address[1], first_Call, sock_for_acks)
    print("exiting thread")
    print("------------------------------------------------------------")
    lock.release()
    return 0

#Decoding, storing and processing the received data in the database
def store_and_process_received_data(message,train_ip, train_port, first_Call, sock_for_acks):
    now = datetime.now()                
    time = now.strftime("%H:%M:%S")         #Getting the current time
    train_data = extract_data(message)      #Extracting meaningful information from the data received.
    if(Trains.find(train_data[1])==(None,None)):   #Checking if the train already exists using the train_number
        if(first_Call == 1):
            Trains.append(train_data, time, train_ip, train_port)     #If the trains does not exit then it appends the data to the end of the linkedlist
            print("New train added")
        else:
            print("Train not authenticated. So discarding packet")
    else:
        my_train = Train_node(train_data, time,train_ip, train_port) 
        if(Trains.find(train_data[1])[1]>my_train.tx_time):                 #Discard old timestamp packets
            print("packet received with old timestamp. So Discarding it")
            return  0
        Trains.update(train_data, time, train_ip, train_port)     #If the train exists in the database then it updates it.
        print("Train details exist and are updated")
    print(" ")
    print("Train currently running: ")
    Trains.display()                        #Print all the currently running trains 
    
    print(" ")
    Trains.show(train_data[1])              #Print all information about the train whose data has just been received (passing the train number)


    my_train = Train_node(train_data, time,train_ip, train_port) 

    if my_train.station2==0:                 #Train is at parking so flush the data
        print(f"Train no{my_train.train_no}   --->>>   REACHED PARKING   --->>>   FLUSHING ITS DATA FROM DATABASE")
        Trains.delete(my_train.train_no)
        print("Train currently running: ")
        Trains.display()                        #Print all the currently running trains 
        return 0

    trains_with_risk_of_collision = Trains.trains_on_same_track(my_train)   #Checking for any other trains within alert distance and on the same track
    if trains_with_risk_of_collision != None:
        send_alert_to_high_collision_risk_trains(trains_with_risk_of_collision, sock_for_acks)
    return 0

def send_alert_to_high_collision_risk_trains(trains_with_risk_of_collision, sock_for_acks):
    tx_message = encrypt_message(STOP_MESSAGE)
    tx_message2 = MIN_BRACKING_DISTANCE_HEAD_ON_COLLISION
    ack_list=[]
    for i in range(len(trains_with_risk_of_collision)):
        train_network_details = Trains.find_train_IP_and_port(trains_with_risk_of_collision[i])
        train_network_details = (train_network_details[0], train_network_details[1] + 1)
        ack_list.append(train_network_details)


        threading.Thread(target=stop_trains, args=(train_network_details,tx_message)).start()
    threading.Thread(target=check_for_acks_and_retransmit_if_needed, args=(trains_with_risk_of_collision,tx_message, sock_for_acks, ack_list)).start()

        # sock.sendto(tx_message, train_network_details)
        # sock.sendto(bin(tx_message2).encode(), train_network_details)
    print("STOP Send to all collision risk trains")
    
def check_for_acks_and_retransmit_if_needed(trains_with_risk_of_collision, tx_message, sock_for_acks, ack_list):
    start_time = time.time()
    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time >= 5:
            print("ack timeout")
            start_time = time.time()
            print(f'Sending stop again to : {ack_list}')
            for i in range(len(ack_list)): 
                threading.Thread(target=stop_trains, args=(ack_list[i],tx_message)).start()
        sock_for_acks.settimeout(ACK_TIMEOUT)
        try:
            data, client = sock_for_acks.recvfrom(4096)      
        except:
            continue
        if(decrypt_message(data) == ACK_MESSAGE_CLIENT):
            data = None
            if client in ack_list:
                print(f'ACS for STOP received from: {client}')
                ack_list.remove(client)
        if(len(ack_list)==0):
            print("exiting ack thread")
            return
        
        




def stop_trains(train_network_details,tx_message):
    sock.sendto(tx_message, train_network_details)

def auth_server(sock_auth_server, sock_auth_client, sock_get_first_data, sock_for_acks):
    print(f"auth thread started...")
    while True:
        # print("Listening for auth")
        data, address = sock_auth_server.recvfrom(4096)
        data = decrypt_message(data)
        if data == CHALLENGE_FROM_CLIENT:
            print("server authenticated")
            sock_auth_server.sendto(encrypt_message(RESPONSE_TO_CLIENT), address)
            time.sleep(0.01)
            print(f"Challenge sent to client; address: {address}")
            sock_auth_server.sendto(encrypt_message(CHALLENGE_FROM_SERVER), address)
            threading.Thread(target=auth_client_check, args=(sock_auth_client, sock_get_first_data, sock_for_acks)).start()
        # return

def auth_client_check(sock_auth_client, sock_get_first_data, sock_for_acks):
    # print("auth client started")
    sock_auth_client.settimeout(AUTH_TIMEOUT)
    try:
        data, address2 = sock_auth_client.recvfrom(4096)
        data = decrypt_message(data)
    except socket.timeout:
        print("auth client sock timeout")
        return
    if data == RESPONSE_TO_SERVER:
        print("client authenticated")
        threading.Thread(target=get_first_data,  args=(address2,sock_get_first_data, sock_for_acks)).start()
        # print("going out of auth_client_check")
        return
    else:
        return
    
def get_first_data(address, sock_get_first_data, sock_for_acks):
    print("get_first_data")
    
    print(f'server address for first packet:{(SERVER_IP, SERVER_PORT+3)}')
    sock_get_first_data.settimeout(AUTH_TIMEOUT*10)
    try:
        data, address2 = sock_get_first_data.recvfrom(4096)
    except socket.timeout:
        print("get_first_data timeout")
        return
    if (address == address2):
        # print("handle client called")
        handle_client(data, sock_get_first_data, address, 1, sock_for_acks)
        # print("going out of get first data")
    return


def check_for_stale_packets(sock_for_acks):
    while(True):
        time.sleep(1)
        now = datetime.now()
        weekday = int(now.isoweekday())
        current_time = ((now.hour)*60*60 + (now.minute)*60 + (now.second))
        trains_on_same_track = []
        train_no=[]
        train_time = []
        try:
            (train_no, train_time) = Trains.running_trains()
        # except:
        #     continue
        finally:
            if(len(train_no)==None):
                continue
        for i in range(len(train_no)):
            # print(f'current time: {current_time}')
            # print(f'train_time: {int(train_time[i])/weekday}')
            print(f'stale packet timeout triggering in: {(current_time-int(train_time[i])/weekday)+11}')
            if ((current_time-int(train_time[i])/weekday)>(STALE_PACKET_TIMEOUT-17)):
                print(f'Stale Packet found, Train number is:{train_no[i]}')
                print("!!!!.........ALERT ALERT ALERT.........!!!!")
                trains_on_same_track.append(train_no[i])

        for i in range(len(trains_on_same_track)):
            temp = Trains.find_other_trains_for_risk_with_stale_packet_trains(trains_on_same_track[i])
            for i in range(len(temp)):
                if(temp[i]) in trains_on_same_track:
                    continue
                trains_on_same_track.append(temp[i])
                


        if(len(trains_on_same_track)!=0):
            print(trains_on_same_track)
            send_alert_to_high_collision_risk_trains(trains_on_same_track, sock_for_acks)
            Trains.delete(trains_on_same_track[i])
        
        # print(f'Running trains after stopping ones with stale packets and their corresponding risky ones: {Trains.display()}')
        

    

global Trains                               #linkedlist containing all the trains
Trains = Train_linked_list()
# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to a specific IP address and port
server_address = (SERVER_IP, SERVER_PORT)
sock.bind(server_address)

sock_auth_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_auth_server.bind((SERVER_IP, SERVER_PORT+1))

sock_auth_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_auth_client.bind((SERVER_IP, SERVER_PORT+2))

sock_get_first_data = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_get_first_data.bind((SERVER_IP, SERVER_PORT+3))

sock_for_acks = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_for_acks.bind((SERVER_IP, SERVER_PORT+4))

threading.Thread(target=auth_server, args=(sock_auth_server,sock_auth_client, sock_get_first_data, sock_for_acks)).start()

if ENABLE_STALE_PACKET_SCAN == True:
    threading.Thread(target=check_for_stale_packets, args=(sock_for_acks,)).start()
print("Waiting for a message...")
while True:
    # print("------------------------------------------------------------")
    # Wait for a message from a client
    # print("Waiting for a message...")
    data, address = sock.recvfrom(4096)

    # Create a new thread to handle the client
    threading.Thread(target=handle_client, args=(data, sock, address, 0, sock_for_acks)).start()