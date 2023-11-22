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
#   Date: 22/11/2023                                                                           #
#   Time: 03:01pm                                                                              #
#   Rev: 1.5                                                                                   #
#   GitHub: https://github.com/Toms-jiji/Kavach/tree/master                                    #
#                                                                                              #
#   Copyright (c) 2023 toms jiji varghese. ALL RIGHTS RESERVED.                                #
#   This code is the sole property of Toms Jiji Varghese and may not be copied, distributed,   #
#   or modified without the express written permission of Toms Jiji Varghese.                  #
################################################################################################                                              

#Variables used to program rfid cards according to test cases

TRAINS_AT_STATIONS_REACHED_PLATFORM = False 
TRAINS_AT_STATIONS_NOT_REACHED_PLATFORM = False
VARIABLE_SPEED_BRAKING = False
FIXED_SPEED_BRAKING = False
HEAD_ON = False
PARKED_TRAIN = False
HIGH_RISK_OF_COLLISION = False
LOW_RISK_OF_COLLISION = False
LOOP_LINE = False
DIFFERENT_TRACK_DIRECTION = False
STOPPED_TRAINS = False
TAIL_END_COLLISION = False


reader = SimpleMFRC522()
is_reading = True

GPIO.setwarnings(False)

# Capture SIGINT for cleanup
def end_read(signal, frame):
    global is_reading
    print('Ctrl+C captured, exiting')
    is_reading = False
    sys.exit()

#function to print all defines and their values
def print_all_def():
    print(f"TRAINS_AT_STATIONS_REACHED_PLATFORM     : {TRAINS_AT_STATIONS_REACHED_PLATFORM}")
    print(f"TRAINS_AT_STATIONS_NOT_REACHED_PLATFORM : {TRAINS_AT_STATIONS_NOT_REACHED_PLATFORM}")
    print(f"VARIABLE_SPEED_BRAKING                  : {VARIABLE_SPEED_BRAKING}")
    print(f"FIXED_SPEED_BRAKING                     : {FIXED_SPEED_BRAKING}")
    print(f"HEAD_ON                                 : {HEAD_ON}")
    print(f"PARKED_TRAIN                            : {PARKED_TRAIN}")
    print(f"HIGH_RISK_OF_COLLISION                  : {HIGH_RISK_OF_COLLISION}")
    print(f"LOW_RISK_OF_COLLISION                   : {LOW_RISK_OF_COLLISION}")  
    print(f"LOOP_LINE                               : {LOOP_LINE}")  
    print(f"DIFFERENT_TRACK_DIRECTION               : {DIFFERENT_TRACK_DIRECTION}")  
    print(f"STOPPED_TRAINS                          : {STOPPED_TRAINS}")  
    print(f"TAIL_END_COLLISION                      : {TAIL_END_COLLISION}")              

#function to create a binary string
def binary(array, size_array):
    string_array        = ""
    for i in range(0,len(array)):
        string_array    = string_array + format(array[i], f"0{size_array[i]}b")
    return int(string_array,2)

#function to write data in rfid
def write_rfid(data):
    temp = data<<len(bin(data))
    data = temp | data              #write data twice so that it is symmetrical
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

#Function to create packet according to test case
def create_packet():
    print("*****************************************")
    print_all_def()
    print("*****************************************")

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

    elif HEAD_ON==True:
        if VARIABLE_SPEED_BRAKING == True:
            if HIGH_RISK_OF_COLLISION == True:
                print("Please scan the first RFID Card for distance-13.....")
                station1 		    = 9010                                  #max 16383
                station2 	    	= 9015                                  #max 16383
                distance 		    = 13                                    #max 63
                loop_line_YN 		= 0                                     #max 1
                loop_line_ID 		= 0                                     #max 1
                track_direction 	= 0                                     #max 1

                size_array          = [14,14,6,1,1, 1]
                array		        = [station1, station2, distance, loop_line_YN, loop_line_ID, track_direction]
                write_rfid(binary(array, size_array))

                input("Press enter to continue")
                print("Please scan the first RFID Card for distance-14.....")
                station1 		    = 9010                                  #max 16383
                station2 	    	= 9015                                  #max 16383
                distance 		    = 14                                    #max 63
                loop_line_YN 		= 0                                     #max 1
                loop_line_ID 		= 0                                     #max 1
                track_direction 	= 0                                     #max 1

                size_array          = [14,14,6,1,1, 1]
                array		        = [station1, station2, distance, loop_line_YN, loop_line_ID, track_direction]
                write_rfid(binary(array, size_array))  
            
            elif LOW_RISK_OF_COLLISION == True:
                print("Please scan the first RFID Card for distance-13.....")
                station1 		    = 9010                                  #max 16383
                station2 	    	= 9015                                  #max 16383
                distance 		    = 1                                     #max 63
                loop_line_YN 		= 0                                     #max 1
                loop_line_ID 		= 0                                     #max 1
                track_direction 	= 0                                     #max 1

                size_array          = [14,14,6,1,1, 1]
                array		        = [station1, station2, distance, loop_line_YN, loop_line_ID, track_direction]
                write_rfid(binary(array, size_array))

                input("Press enter to continue")
                print("Please scan the first RFID Card for distance-14.....")
                station1 		    = 9010                                  #max 16383
                station2 	    	= 9015                                  #max 16383
                distance 		    = 50                                    #max 63
                loop_line_YN 		= 0                                     #max 1
                loop_line_ID 		= 0                                     #max 1
                track_direction 	= 0                                     #max 1

                size_array          = [14,14,6,1,1, 1]
                array		        = [station1, station2, distance, loop_line_YN, loop_line_ID, track_direction]
                write_rfid(binary(array, size_array))  
        if FIXED_SPEED_BRAKING == True:
            if HIGH_RISK_OF_COLLISION == True:
                print("Please scan the first RFID Card for distance-13.....")
                station1 		    = 9010                                  #max 16383
                station2 	    	= 9015                                  #max 16383
                distance 		    = 13                                    #max 63
                loop_line_YN 		= 0                                     #max 1
                loop_line_ID 		= 0                                     #max 1
                track_direction 	= 0                                     #max 1

                size_array          = [14,14,6,1,1, 1]
                array		        = [station1, station2, distance, loop_line_YN, loop_line_ID, track_direction]
                write_rfid(binary(array, size_array))

                input("Press enter to continue")
                print("Please scan the first RFID Card for distance-17.....")
                station1 		    = 9010                                  #max 16383
                station2 	    	= 9015                                  #max 16383
                distance 		    = 17                                    #max 63
                loop_line_YN 		= 0                                     #max 1
                loop_line_ID 		= 0                                     #max 1
                track_direction 	= 0                                     #max 1

                size_array          = [14,14,6,1,1, 1]
                array		        = [station1, station2, distance, loop_line_YN, loop_line_ID, track_direction]
                write_rfid(binary(array, size_array))          
            elif LOW_RISK_OF_COLLISION == True:
                print("Please scan the first RFID Card for distance-13.....")
                station1 		    = 9010                                  #max 16383
                station2 	    	= 9015                                  #max 16383
                distance 		    = 13                                    #max 63
                loop_line_YN 		= 0                                     #max 1
                loop_line_ID 		= 0                                     #max 1
                track_direction 	= 0                                     #max 1

                size_array          = [14,14,6,1,1, 1]
                array		        = [station1, station2, distance, loop_line_YN, loop_line_ID, track_direction]
                write_rfid(binary(array, size_array))

                input("Press enter to continue")
                print("Please scan the first RFID Card for distance-50.....")
                station1 		    = 9010                                  #max 16383
                station2 	    	= 9015                                  #max 16383
                distance 		    = 50                                    #max 63
                loop_line_YN 		= 0                                     #max 1
                loop_line_ID 		= 0                                     #max 1
                track_direction 	= 0                                     #max 1

                size_array          = [14,14,6,1,1, 1]
                array		        = [station1, station2, distance, loop_line_YN, loop_line_ID, track_direction]
                write_rfid(binary(array, size_array))  

    elif PARKED_TRAIN==True:
        print("Please scan the first RFID Card for for running train.....")
        station1 		    = 9010                                  #max 16383
        station2 	    	= 9011                                  #max 16383
        reached_platform_YN = 0                                     #max 1
        platform_ID 		= 0                                     #max 31
        platform_entry_YN 	= 0                                     #max 1

        size_array          = [14,14,1,5,1]
        array		        = [station1, station2, reached_platform_YN, platform_ID, platform_entry_YN]
        write_rfid(binary(array, size_array))

        input("Press enter to continue")
        print("Please scan the second RFID Card for parking location.....")
        station1 		    = 9011                                  #max 16383
        station2 	    	= 0                                     #max 16383
        reached_platform_YN = 1                                     #max 1
        platform_ID 		= 7                                     #max 31
        platform_entry_YN 	= 0                                     #max 1

        size_array          = [14,14,1,5,1]
        array		        = [station1, station2, reached_platform_YN, platform_ID, platform_entry_YN]
        write_rfid(binary(array, size_array))

    elif DIFFERENT_TRACK_DIRECTION==True:
        print("Please scan the first RFID Card for distance-13.....")
        station1 		    = 9010                                  #max 16383
        station2 	    	= 9015                                  #max 16383
        distance 		    = 13                                    #max 63
        loop_line_YN 		= 0                                     #max 1
        loop_line_ID 		= 0                                     #max 1
        track_direction 	= 1                                     #max 1

        size_array          = [14,14,6,1,1, 1]
        array		        = [station1, station2, distance, loop_line_YN, loop_line_ID, track_direction]
        write_rfid(binary(array, size_array))

        input("Press enter to continue")
        print("Please scan the first RFID Card for distance-14.....")
        station1 		    = 9010                                  #max 16383
        station2 	    	= 9015                                  #max 16383
        distance 		    = 14                                    #max 63
        loop_line_YN 		= 0                                     #max 1
        loop_line_ID 		= 0                                     #max 1
        track_direction 	= 0                                     #max 1

        size_array          = [14,14,6,1,1, 1]
        array		        = [station1, station2, distance, loop_line_YN, loop_line_ID, track_direction]
        write_rfid(binary(array, size_array))  

    elif LOOP_LINE == True:
        print("Please scan the first RFID Card for distance-13.....")
        station1 		    = 9010                                  #max 16383
        station2 	    	= 9015                                  #max 16383
        distance 		    = 13                                    #max 63
        loop_line_YN 		= 0                                     #max 1
        loop_line_ID 		= 0                                     #max 1
        track_direction 	= 0                                     #max 1

        size_array          = [14,14,6,1,1, 1]
        array		        = [station1, station2, distance, loop_line_YN, loop_line_ID, track_direction]
        write_rfid(binary(array, size_array))

        input("Press enter to continue")
        print("Please scan the first RFID Card for distance-14.....")
        station1 		    = 9010                                  #max 16383
        station2 	    	= 9015                                  #max 16383
        distance 		    = 14                                    #max 63
        loop_line_YN 		= 1                                     #max 1
        loop_line_ID 		= 1                                     #max 1
        track_direction 	= 0                                     #max 1

        size_array          = [14,14,6,1,1, 1]
        array		        = [station1, station2, distance, loop_line_YN, loop_line_ID, track_direction]
        write_rfid(binary(array, size_array)) 

    elif STOPPED_TRAINS == True:
        print("Please scan the first RFID Card for distance-13.....")
        station1 		    = 9010                                  #max 16383
        station2 	    	= 9015                                  #max 16383
        distance 		    = 13                                    #max 63
        loop_line_YN 		= 0                                     #max 1
        loop_line_ID 		= 0                                     #max 1
        track_direction 	= 0                                     #max 1

        size_array          = [14,14,6,1,1, 1]
        array		        = [station1, station2, distance, loop_line_YN, loop_line_ID, track_direction]
        write_rfid(binary(array, size_array))

        input("Press enter to continue")
        print("Please scan the first RFID Card for distance-14.....")
        station1 		    = 9010                                  #max 16383
        station2 	    	= 9015                                  #max 16383
        distance 		    = 14                                    #max 63
        loop_line_YN 		= 0                                     #max 1
        loop_line_ID 		= 0                                     #max 1
        track_direction 	= 0                                     #max 1

        size_array          = [14,14,6,1,1, 1]
        array		        = [station1, station2, distance, loop_line_YN, loop_line_ID, track_direction]
        write_rfid(binary(array, size_array)) 
        print("PLEASE MAKE SURE THE INDIVIDUAL TRAIN SPEEDS ARE 0..!!!")

    elif TAIL_END_COLLISION == True:
        print("Please scan the first RFID Card for distance-13.....")
        station1 		    = 9010                                  #max 16383
        station2 	    	= 9015                                  #max 16383
        distance 		    = 13                                    #max 63
        loop_line_YN 		= 0                                     #max 1
        loop_line_ID 		= 0                                     #max 1
        track_direction 	= 0                                     #max 1

        size_array          = [14,14,6,1,1, 1]
        array		        = [station1, station2, distance, loop_line_YN, loop_line_ID, track_direction]
        write_rfid(binary(array, size_array))

        input("Press enter to continue")
        print("Please scan the first RFID Card for distance-14.....")
        station1 		    = 9010                                  #max 16383
        station2 	    	= 9015                                  #max 16383
        distance 		    = 14                                    #max 63
        loop_line_YN 		= 0                                     #max 1
        loop_line_ID 		= 0                                     #max 1
        track_direction 	= 0                                     #max 1

        size_array          = [14,14,6,1,1, 1]
        array		        = [station1, station2, distance, loop_line_YN, loop_line_ID, track_direction]
        write_rfid(binary(array, size_array)) 
        print("PLEASE MAKE SURE THAT THE TRAIN DIRECTIONS ARE SAME AND THEIR SPEEDS ARE DIFFERENT AND ENABLE FIXED BRAKING..!!!")

#Function to create a trampered rfid card
def write_tampered_rfid(data):
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

#create a tampered rfid card data
def tampered_rfid():
    print("Please scan the first RFID Card for distance-14.....")
    station1 		    = 9010                                  #max 16383
    station2 	    	= 9015                                  #max 16383
    distance 		    = 14                                    #max 63
    loop_line_YN 		= 0                                     #max 1
    loop_line_ID 		= 0                                     #max 1
    track_direction 	= 0                                     #max 1
    size_array          = [14,14,6,1,1, 1]
    array		        = [station1, station2, distance, loop_line_YN, loop_line_ID, track_direction]
    write_tampered_rfid(binary(array, size_array)) 

print("\n\nWhich situation do you need to simulate?:")
print("a. HEAD ON")
print("b. PARKED TRAIN")
print("c. LOOP_LINE")
print("d. DIFFERENT_TRACK_DIRECTION")
print("e. TRAINS_AT_STATIONS_REACHED_PLATFORM")
print("f. TRAINS_AT_STATIONS_NOT_REACHED_PLATFORM")
print("g. STOPPED_TRAINS")
print("h. TAIL END COLLISION")
print("i. TAMPERED/UNKNOWN RFID CARD")

case1 = input("\nPlease enter one the above options: ")

if(case1 == 'a'):
    print("  a. VARIABLE SPEED BRAKING")
    print("  b. FIXED SPEED BRAKING")
    case2 = input("\n  Please enter one the above options: ")
    if(case2 == 'a'):
        print("    a. HIGH RISK OF COLLISION")
        print("    b. LOW RISK OF COLLISION")
        case3 = input("\n    Please enter one the above options: ")
        if(case3 == 'a'):
            TRAINS_AT_STATIONS_REACHED_PLATFORM = False
            TRAINS_AT_STATIONS_NOT_REACHED_PLATFORM = False
            VARIABLE_SPEED_BRAKING = True
            FIXED_SPEED_BRAKING = False
            HEAD_ON = True
            PARKED_TRAIN = False
            HIGH_RISK_OF_COLLISION = True
            LOW_RISK_OF_COLLISION = False
            LOOP_LINE = False
            DIFFERENT_TRACK_DIRECTION = False
            STOPPED_TRAINS = False
            TAIL_END_COLLISION = False
        if(case3 == 'b'):
            TRAINS_AT_STATIONS_REACHED_PLATFORM = False
            TRAINS_AT_STATIONS_NOT_REACHED_PLATFORM = False
            VARIABLE_SPEED_BRAKING = True
            FIXED_SPEED_BRAKING = False
            HEAD_ON = True
            PARKED_TRAIN = False
            HIGH_RISK_OF_COLLISION = False
            LOW_RISK_OF_COLLISION = True
            LOOP_LINE = False
            DIFFERENT_TRACK_DIRECTION = False
            STOPPED_TRAINS = False
            TAIL_END_COLLISION = False
    if(case2 == 'b'):
        print("    a. HIGH RISK OF COLLISION")
        print("    b. LOW RISK OF COLLISION")
        case3 = input("\n    Please enter one the above options: ")
        if(case3 == 'a'):
            TRAINS_AT_STATIONS_REACHED_PLATFORM = False
            TRAINS_AT_STATIONS_NOT_REACHED_PLATFORM = False
            VARIABLE_SPEED_BRAKING = False
            FIXED_SPEED_BRAKING = True
            HEAD_ON = True
            PARKED_TRAIN = False
            HIGH_RISK_OF_COLLISION = True
            LOW_RISK_OF_COLLISION = False
            LOOP_LINE = False
            DIFFERENT_TRACK_DIRECTION = False
            STOPPED_TRAINS = False
            TAIL_END_COLLISION = False
        if(case3 == 'b'):
            TRAINS_AT_STATIONS_REACHED_PLATFORM = False
            TRAINS_AT_STATIONS_NOT_REACHED_PLATFORM = False
            VARIABLE_SPEED_BRAKING = False
            FIXED_SPEED_BRAKING = True
            HEAD_ON = True
            PARKED_TRAIN = False
            HIGH_RISK_OF_COLLISION = False
            LOW_RISK_OF_COLLISION = True
            LOOP_LINE = False
            DIFFERENT_TRACK_DIRECTION = False
            STOPPED_TRAINS = False
            TAIL_END_COLLISION = False

if(case1 == 'b'):
    TRAINS_AT_STATIONS_REACHED_PLATFORM = False
    TRAINS_AT_STATIONS_NOT_REACHED_PLATFORM = False
    VARIABLE_SPEED_BRAKING = False
    FIXED_SPEED_BRAKING = False
    HEAD_ON = False
    PARKED_TRAIN = True
    HIGH_RISK_OF_COLLISION = False
    LOW_RISK_OF_COLLISION = False
    DIFFERENT_TRACK_DIRECTION = False
    STOPPED_TRAINS = False
    TAIL_END_COLLISION = False

if(case1 == "c"):
    TRAINS_AT_STATIONS_REACHED_PLATFORM = False
    TRAINS_AT_STATIONS_NOT_REACHED_PLATFORM = False
    VARIABLE_SPEED_BRAKING = False
    FIXED_SPEED_BRAKING = False
    HEAD_ON = False
    PARKED_TRAIN = False
    HIGH_RISK_OF_COLLISION = False
    LOW_RISK_OF_COLLISION = False
    LOOP_LINE = True
    DIFFERENT_TRACK_DIRECTION = False
    STOPPED_TRAINS = False
    TAIL_END_COLLISION = False

if(case1 == "d"):
    TRAINS_AT_STATIONS_REACHED_PLATFORM = False
    TRAINS_AT_STATIONS_NOT_REACHED_PLATFORM = False
    VARIABLE_SPEED_BRAKING = False
    FIXED_SPEED_BRAKING = False
    HEAD_ON = False
    PARKED_TRAIN = False
    HIGH_RISK_OF_COLLISION = False
    LOW_RISK_OF_COLLISION = False
    LOOP_LINE = False
    DIFFERENT_TRACK_DIRECTION = True
    STOPPED_TRAINS = False
    TAIL_END_COLLISION = False

if(case1 == "e"):
    TRAINS_AT_STATIONS_REACHED_PLATFORM = True
    TRAINS_AT_STATIONS_NOT_REACHED_PLATFORM = False
    VARIABLE_SPEED_BRAKING = False
    FIXED_SPEED_BRAKING = False
    HEAD_ON = False
    PARKED_TRAIN = False
    HIGH_RISK_OF_COLLISION = False
    LOW_RISK_OF_COLLISION = False
    LOOP_LINE = False
    DIFFERENT_TRACK_DIRECTION = False
    STOPPED_TRAINS = False
    TAIL_END_COLLISION = False

if(case1 == "f"):
    TRAINS_AT_STATIONS_REACHED_PLATFORM = False
    TRAINS_AT_STATIONS_NOT_REACHED_PLATFORM = True
    VARIABLE_SPEED_BRAKING = False
    FIXED_SPEED_BRAKING = False
    HEAD_ON = False
    PARKED_TRAIN = False
    HIGH_RISK_OF_COLLISION = False
    LOW_RISK_OF_COLLISION = False
    LOOP_LINE = False
    DIFFERENT_TRACK_DIRECTION = False
    STOPPED_TRAINS = False
    TAIL_END_COLLISION = False

if(case1 == "g"):
    TRAINS_AT_STATIONS_REACHED_PLATFORM = False
    TRAINS_AT_STATIONS_NOT_REACHED_PLATFORM = False
    VARIABLE_SPEED_BRAKING = False
    FIXED_SPEED_BRAKING = False
    HEAD_ON = False
    PARKED_TRAIN = False
    HIGH_RISK_OF_COLLISION = False
    LOW_RISK_OF_COLLISION = False
    LOOP_LINE = False
    DIFFERENT_TRACK_DIRECTION = False
    STOPPED_TRAINS = True
    TAIL_END_COLLISION = False

if(case1 == "h"):
    TRAINS_AT_STATIONS_REACHED_PLATFORM = False
    TRAINS_AT_STATIONS_NOT_REACHED_PLATFORM = False
    VARIABLE_SPEED_BRAKING = False
    FIXED_SPEED_BRAKING = False
    HEAD_ON = False
    PARKED_TRAIN = False
    HIGH_RISK_OF_COLLISION = False
    LOW_RISK_OF_COLLISION = False
    LOOP_LINE = False
    DIFFERENT_TRACK_DIRECTION = False
    STOPPED_TRAINS = False
    TAIL_END_COLLISION = True

if(case1 == 'i'):
    tampered_rfid() #create a tampered rfid
    sys.exit()      #exit the program

create_packet()     #create packet and program the rfid    
