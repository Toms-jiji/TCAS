import socket
import time
from datetime import datetime
import random
from cryptography.fernet import Fernet
from random import randint
import threading

################################################################################################
#   Author: Toms Jiji Varghese                                                                 #
#   Date: 19/11/2023                                                                           #
#   Time: 11:57pm                                                                              #
#   Rev: 1.2                                                                                   #
#   GitHub: https://github.com/Toms-jiji/Kavach/tree/master                                    #
#                                                                                              #
#   Copyright (c) 2023 toms jiji varghese. ALL RIGHTS RESERVED.                                #
#   This code is the sole property of Toms Jiji Varghese and may not be copied, distributed,   #
#   or modified without the express written permission of Toms Jiji Varghese.                  #
################################################################################################ 

RANDOM_DATA = False                      #Generates packet using a random number generator                                                           

TRAINS_AT_STATIONS = False               #Generated packets for trains which are currently at a station
TRAIN_AT_PARKING_LOT = False             #Generated packets for trains which are currently at a parking/storage space -->TRAIN_AT_PARKING_LOT_TRIGGER should be True
TRAIN_AT_PARKING_LOT_TRIGGER = False     #Trigger for parking lot condition.
ONE_TRAIN_IN_LOOP_LINE = False           #Generated packets such that one of the trains is in a loop line


FIXED_DISTANCE = False                   #True -> Braking is based on a predefine distance ; False -> Braking is based on the relative speed
HEAD_ON = True                          #Trains are going opposite to each other
TRAINS_GOING_AWAY = True                #Trains are going away
TAIL_END = False                        #Trail end collision condition    


TRAINS_AT_STATIONS_NOT_REACHED_PLATFORM = True
TRAINS_AT_STATIONS_REACHED_PLATFORM = False
BETWEEN_SAME_STATION = False             #Generated packets with different station1 and station 2

reader = SimpleMFRC522()
is_reading = True

GPIO.setwarnings(False)

# Capture SIGINT for cleanup
def end_read(signal, frame):
    global is_reading
    print('Ctrl+C captured, exiting')
    is_reading = False
    sys.exit()

def print_all_def():
    print(f"BETWEEN_SAME_STATION                    : {BETWEEN_SAME_STATION}")
    print(f"TRAINS_AT_STATIONS                      : {TRAINS_AT_STATIONS}")
    print(f"TRAIN_AT_PARKING_LOT                    : {TRAIN_AT_PARKING_LOT}")
    print(f"TRAIN_AT_PARKING_LOT_TRIGGER            : {TRAIN_AT_PARKING_LOT_TRIGGER}")
    print(f"ONE_TRAIN_IN_LOOP_LINE                     : {ONE_TRAIN_IN_LOOP_LINE}")
    print(f"VARIABLE_DISTANCE                       : {VARIABLE_DISTANCE}")
    print(f"FIXED_DISTANCE                          : {FIXED_DISTANCE}")
    print(f"HEAD_ON                                 : {HEAD_ON}")
    print(f"TAIL_END                                : {TAIL_END}")           

def int_to_binary(num, bits):
    return format(num, f"0{bits}b")

def extract_bits(message, extract_bits, left_shift_by):
    return (message >> left_shift_by) & (2**(extract_bits)-1)

def binary(array, size_array):
    string_array        = ""
    for i in range(0,len(array)):
        string_array    = string_array + format(array[i], f"0{size_array[i]}b")
    return int(string_array,2)

def write_rfid(data):
    temp = data<<len(bin(data))
    data = temp | data
    # Hook the SIGINT
    signal.signal(signal.SIGINT, end_read)
    GPIO.setwarnings(False)
    GPIO.cleanup()    
    try:
        print("Place RFID card near the reader...")
        reader.write(str(data))
        data_read = reader.read()
        print(f'RFID data: {data_read[1]}')
    finally:
        GPIO.cleanup()
    return

def create_packet():
    if TRAINS_AT_STATIONS_NOT_REACHED_PLATFORM==True:
        print("Please scan the first RFID Card for branch-23.....")
        now = datetime.now()
        station1 		    = 9010                                  #max 16383
        station2 	    	= 9010                                  #max 16383
        reached_platform_YN = 0                                     #max 1
        branch_ID 		    = 23                                    #max 63

        size_array          = [14,14,1,6]
        array		        = [station1, station2, reached_platform_YN, branch_ID]
        write_rfid(binary(array, size_array))
    
        input("Press enter to continue")
        print("Please scan the second RFID Card for branch-45.....")
        now = datetime.now()
        station1 		    = 9010                                  #max 16383
        station2 	    	= 9010                                  #max 16383
        reached_platform_YN = 0                                     #max 1
        branch_ID 		    = 45                                    #max 63

        size_array          = [14,14,1,6]
        array		        = [station1, station2, reached_platform_YN, branch_ID]
        write_rfid(binary(array, size_array))
    
    elif TRAINS_AT_STATIONS_REACHED_PLATFORM==True:
        print("Please scan the first RFID Card for platform-3.....")
        station1 		    = 9010                                  #max 16383
        station2 	    	= 9010                                  #max 16383
        reached_platform_YN = 1                                     #max 1
        platform_ID 		= 3                                     #max 31
        platform_entry_YN 	= 0                                     #max 1

        size_array          = [14,14,1,5,1]
        array		        = [station1, station2, reached_platform_YN, platform_ID, platform_entry_YN]
        write_rfid(binary(array, size_array))

        input("Press enter to continue")
        print("Please scan the second RFID Card for platform-7.....")
        station1 		    = 9010                                  #max 16383
        station2 	    	= 9010                                  #max 16383
        reached_platform_YN = 1                                     #max 1
        platform_ID 		= 7                                     #max 31
        platform_entry_YN 	= 0                                     #max 1

        size_array          = [14,14,1,5,1]
        array		        = [station1, station2, reached_platform_YN, platform_ID, platform_entry_YN]
        write_rfid(binary(array, size_array))

    elif BETWEEN_SAME_STATION == True:
        print("Please scan the first RFID Card for distance-13.....")
        station1 		    = 9010                                  #max 16383
        station2 	    	= 9015                                  #max 16383
        distance 		    = 13                                    #max 63
        loop_line_YN 		= 1                                     #max 1  -- first loopline after the rfid with distance 23
        loop_line_ID 		= 0                                     #max 1  -- Not required
        track_direction 	= 0                                     #max 1

        size_array          = [14,14,6,1,1, 1]
        array		        = [station1, station2, distance, loop_line_YN, loop_line_ID, track_direction]
        write_rfid(binary(array, size_array))

        input("Press enter to continue")
        print("Please scan the first RFID Card for distance-14.....")
        station1 		    = 9010                                  #max 16383
        station2 	    	= 9015                                  #max 16383
        distance 		    = 14                                    #max 63
        loop_line_YN 		= 1                                     #max 1  -- first loopline after the rfid with distance 23
        loop_line_ID 		= 0                                     #max 1  -- Not required
        track_direction 	= 0                                     #max 1

        size_array          = [14,14,6,1,1, 1]
        array		        = [station1, station2, distance, loop_line_YN, loop_line_ID, track_direction]
        write_rfid(binary(array, size_array))  

print("\n\nWhich situation do you need to simulate?:")
case = input("a. BETWEEN_SAME_STATION \nb. TRAINS_AT_STATIONS_REACHED_PLATFORM \nc. TRAINS_AT_STATIONS_NOT_REACHED_PLATFORMv \n\nPlease enter one the above options: ")
if (case == "a"):
    BETWEEN_SAME_STATION = True
    TRAINS_AT_STATIONS_REACHED_PLATFORM = False
    TRAINS_AT_STATIONS_NOT_REACHED_PLATFORM = False
elif (case == "b"):
    BETWEEN_SAME_STATION = False
    TRAINS_AT_STATIONS_REACHED_PLATFORM = True
    TRAINS_AT_STATIONS_NOT_REACHED_PLATFORM = False
elif (case == "c"):
    BETWEEN_SAME_STATION = False
    TRAINS_AT_STATIONS_REACHED_PLATFORM = False
    TRAINS_AT_STATIONS_NOT_REACHED_PLATFORM = True
create_packet()
