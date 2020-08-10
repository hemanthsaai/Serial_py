#Import required Modules
import Crc_calc
import My_Serial
import struct
import os
import sys

#BOOTLOADER COMMUNICATOR V1.0
#HemanthjSai

#MACRO DEFINITIONS
CMD_BOOTLOADER_GET_VERSION      = 0xB1      #get Bootloader Version
CMD_BOOTLOADER_GET_CHIP_ID      = 0xB2      #get chip identification number
CMD_BOOTLOADER_ERASE_APPLI      = 0xB3      #erase Application
CMD_BOOTLOADER_FLASH_APPLI      = 0xB4      #flash Application
CMD_BOOTLOADER_INTEG_CHECK      = 0xB5      #check Integrity
CMD_BOOTLOADER_JUMPTO_APPL      = 0xB6      #Jump to flashed Application
CMD_TEST                        = 0xB7      #Specific for new implementation testing

TXT_BOOTLOADER_GET_VERSION      = "CMD_BOOTLOADER_GET_VERSION"
TXT_BOOTLOADER_GET_CHIP_ID      = "CMD_BOOTLOADER_GET_CHIP_ID"
TXT_BOOTLOADER_ERASE_APPLI      = "CMD_BOOTLOADER_ERASE_APPLI"
TXT_BOOTLOADER_FLASH_APPLI      = "CMD_BOOTLOADER_FLASH_APPLI"
TXT_BOOTLOADER_INTEG_CHECK      = "CMD_BOOTLOADER_INTEG_CHECK"
TXT_BOOTLOADER_JUMPTO_APPL      = "CMD_BOOTLOADER_JUMPTO_APPL"
TXT_TEST                        = "EXECUTE TEST COMMAND"

LEN_BOOTLOADER_GET_VERSION      = 0x1
LEN_BOOTLOADER_GET_CHIP_ID      = 0x4
LEN_BOOTLOADER_ERASE_APPLI      = 0x1
LEN_BOOTLOADER_FLASH_APPLI      = 0x1
LEN_BOOTLOADER_INTEG_CHECK      = 0x1
LEN_TEST                        = 0x1
LEN_OF_ACK                         = 0x1 

PASS                            = 0x1
FAIL                            = 0x0

BL_ACK                          = 0xA5  #If the command is executed properly (Currently only CRC check)
BL_NACK                         = 0xA6  #If an error occurs (Currently only CRC ERROR)

#The BIN will be split to packets, each of length defined here
BL_MAX_APPL_PACK_LIM            = 256

##Global Variables
user_ip = ""
transmit_data = []
packet_count = 0


#Generic function which takes the byte list of data and
#adds CRC to the end of list
#Transmits the data and verifies the acknowledement
def Transmit_a_packet(packet):
    #Add CRC to the packet
    crc_value = Crc_calc.calc_Crc32Mpeg2(packet,len(packet))
    Crc_to_byte = My_Serial.word_to_bytelist(crc_value, My_Serial.hex_len(crc_value))
    for element in Crc_to_byte:
        packet.append(element)
    print(packet)

    #With CRC at end of Packett, We are ready for Transmission
    for element in packet:
        #Transmit Byte after Byte 
        My_Serial.Write_to_serial_port(element)
    #Take the acknowledement and  ensure the packet is sucessfully transfered
    status = My_Serial.Read_from_serial_port(LEN_OF_ACK)
    if status == struct.pack('>B',BL_ACK):
        #Received S
        print("PACKET Flashed ") 
        return PASS
    elif status == struct.pack('>B',BL_NACK):
        print("FAILED TO FLASH PACKET ")
        return FAIL
    else:
        print("Invalid Status Received while Flashing Packet:  " + str(status))
        return FAIL

#After the BIN is split to packets, before transmisssion we have to first send 
#the length of the packet to STM, then STM will configure UART 
#to receive sent number of bytes
#
#This function is called before transmitting every packet. 
#Also before the whole BIN indicating Number of packets
def Transmit_a_Length_packet(length):
    Length_Packet = []
    #first append the Command of Bootloader
    Length_Packet.append(CMD_BOOTLOADER_FLASH_APPLI)
    #Append the Length to the packet now
    len_count = My_Serial.hex_len(length)
    byte_list = My_Serial.word_to_bytelist(length, len_count)
    for byte in byte_list:
        Length_Packet.append(byte)   
    #As the size of packet Length field is 2 bytes,         
    #Append 0's in remaining bytes if len is not 2 bytes
    if len_count != 2:
        Length_Packet.append(0x0)
    #Now we are ready for Transmission
    #this function call will add CRC at end and transmit the packet.
    #Also it takes care of Acknowledge
    Transmit_a_packet(Length_Packet)
    Length_Packet.clear()    

def process_bin():
    transmit_data.clear()
    #First Calculate Size of binary
    binary = open("Application.bin","rb")
    byte = binary.read(1)
    byte_count = 0
    while byte:
        byte = binary.read(1)
        byte_count = byte_count + 1
    binary.close()
    print("Total byets in BIN is :  " + str(byte_count))
    
    #now each pack is with BL_MAX_APPL_PACK_LIM bytes 
    #so calculate number of total packets to transfer by spliting the BIN
    Num_Packets = int(byte_count / BL_MAX_APPL_PACK_LIM) + 1
    print("Num of packts to transfer : " + str(Num_Packets))
    Transmit_a_Length_packet(Num_Packets)
    
    #As No of packets is configured by both TX and RX
    #reopen the binary to start making packets
    #Each appl_packet of length BL_MAX_APPL_PACK_LIM bytes
    binary = open("Application.bin","rb")
    appl_packet = []
    byte_count = 0
    global packet_count
    #read the binary byte by byte and append to a list
    byte = binary.read(1)
    while byte:
        #Bytes read from file are already in Binary format, Lets Unpack them first 
        #as we have to calculate CRC
        byte = struct.unpack('>B',byte)
        appl_packet.append(byte[0])
        byte_count = byte_count + 1
        #once the list size reaches BL_MAX_APPL_PACK_LIM bytes
        #then calculate CRC for the appl_packet and transmit it
        if byte_count == BL_MAX_APPL_PACK_LIM:
            #ALL READY FOR TRANSMISSION
            Transmit_a_Length_packet(byte_count + 4) # 4 extra for CRC
            Transmit_a_packet(appl_packet)
            #clear the appl_packet so we can frame a fresh appl_packet from binary
            byte_count = 0
            appl_packet.clear()
            packet_count = packet_count + 1
        byte = binary.read(1)
        

    #last appl_packet may not be full, so we have to process it separetely now 
    #process it separetely now
    Transmit_a_Length_packet(byte_count + 4)
    Transmit_a_packet(appl_packet)
    packet_count = packet_count + 1
    print(packet_count)
    


def menu_list():
    global port 
    global user_ip
    os.system("cls")
    print(" _____________________________________________________________________________________________ ")
    print("|  ____                 _    _                        _                _____   ____   __  __  |")
    print("| |  _ \               | |  | |                      | |              / ____| / __ \ |  \/  | |")
    print("| | |_) |  ___    ___  | |_ | |      ___    __ _   __| |  ___  _ __  | |     | |  | || \  / | |")
    print("| |  _ <  / _ \  / _ \ | __|| |     / _ \  / _` | / _` | / _ \| '__| | |     | |  | || |\/| | |")
    print("| | |_) || (_) || (_) || |_ | |____| (_) || (_| || (_| ||  __/| |    | |____ | |__| || |  | | |")
    print("| |____/  \___/  \___/  \__||______|\___/  \__,_| \__,_| \___||_|     \_____| \____/ |_|  |_| |")
    print("|_____________________________________________________________________________________________|")
    print("|                                      V1.0 hemanth j. sai                                    |")
    print("|_____________________________________________________________________________________________|")
    port_list = My_Serial.Identify_Open_COM_PORTS()
    count = 0
    if port_list:
        print("|    Menu:  Select a COM PORT from available list                                             |")
        for port in port_list:
            print("|    " +  str(count+1) +  ". "  + port + " "*82 + "|")
        print("|" + "_"*93 + "|")
        user_ip = int(input("|    Provide Input : "))
        if user_ip <= len(port_list):
            port = My_Serial.open_serial_port(port_list[user_ip-1])
        else:
            print("|    Invalid Input. Please Try again" + " "*58   + "|")
            print("|" + "_"*93 + "|")
            return FAIL
    else:
        print("| No COM PORTS are available to open. Please Try again" + " "*40 + "|")
        print("|" + "_"*93 + "|")
        return FAIL
    if port:
        print("|    " +  port_list[user_ip-1] + " Selected and Opened, Ready to Use" + " "*51 + "|")
        My_Serial.open_port = port
    else:
        print("|    Failed to Open Port" +  port_list[user_ip-1] +  " "*65 + "|")
        print("|" + "_"*93 + "|")
        return FAIL
    print("|" + "_"*93 + "|")
    print("|    1:  " + TXT_BOOTLOADER_GET_VERSION +   " "*59 + "|")
    print("|    2:  " + TXT_BOOTLOADER_GET_CHIP_ID +   " "*59 + "|")
    print("|    3:  " + TXT_BOOTLOADER_ERASE_APPLI +   " "*59 + "|")
    print("|    4:  " + TXT_BOOTLOADER_FLASH_APPLI +   " "*59 + "|")
    print("|    5:  " + TXT_BOOTLOADER_INTEG_CHECK +   " "*59 + "|")
    print("|    6:  " + TXT_BOOTLOADER_JUMPTO_APPL +   " "*59 + "|")  
    print("|    7:  " + TXT_TEST +   " "*65 + "|")
    print("|" + "_"*93 + "|")
    user_ip = int(input("|    Provide Input : ")) + 0xB0
    print("|" + "_"*93 + "|")
    return PASS

    
menu_list()
if user_ip == CMD_BOOTLOADER_GET_VERSION:
    transmit_data = My_Serial.word_to_bytelist(CMD_BOOTLOADER_GET_VERSION, My_Serial.hex_len(CMD_BOOTLOADER_GET_VERSION))
    crc_value = Crc_calc.calc_Crc32Mpeg2(transmit_data,len(transmit_data))
    crc_value = My_Serial.word_to_bytelist(crc_value, My_Serial.hex_len(crc_value) )
    for element in crc_value:
        transmit_data.append(element)
        
    for byte in transmit_data:
        My_Serial.Write_to_serial_port(byte)
        
    status = My_Serial.get_ACK()
    if status == PASS:
        ver = My_Serial.Read_from_serial_port(LEN_BOOTLOADER_GET_VERSION)
        print("|    Boot Loader Version Number : " + str(int(ver[0])) + " "*58 + "|")
    else:
        print("|    Invalid CRC Received           "  + " "*58 + "|")
    
elif user_ip == CMD_BOOTLOADER_GET_CHIP_ID:
    transmit_data = My_Serial.word_to_bytelist(CMD_BOOTLOADER_GET_CHIP_ID, My_Serial.hex_len(CMD_BOOTLOADER_GET_CHIP_ID))
    crc_value = Crc_calc.calc_Crc32Mpeg2(transmit_data,len(transmit_data))
    crc_value = My_Serial.word_to_bytelist(crc_value, My_Serial.hex_len(crc_value) )
    for element in crc_value:
        transmit_data.append(element)
        
    for byte in transmit_data:
        My_Serial.Write_to_serial_port(byte)
        
    status = My_Serial.get_ACK()

    cid = My_Serial.Read_from_serial_port(LEN_BOOTLOADER_GET_CHIP_ID)
    cid = cid[0]<<24 | cid[1] << 16 | cid[2] <<8 | cid[3]
    print("|    Chip Identification Number : " + str(cid) + " "*51 + "|")
    #print(transmit_data)
    
elif user_ip == CMD_BOOTLOADER_ERASE_APPLI:
    transmit_data = My_Serial.word_to_bytelist(CMD_BOOTLOADER_ERASE_APPLI, My_Serial.hex_len(CMD_BOOTLOADER_ERASE_APPLI))
    crc_value = Crc_calc.calc_Crc32Mpeg2(transmit_data,len(transmit_data))
    crc_value = My_Serial.word_to_bytelist(crc_value, My_Serial.hex_len(crc_value) )
    for element in crc_value:
        transmit_data.append(element)
        
    for byte in transmit_data:
        My_Serial.Write_to_serial_port(byte)
        
    status = My_Serial.get_ACK()

    status = My_Serial.Read_from_serial_port(LEN_BOOTLOADER_ERASE_APPLI)
    status = struct.unpack('>B',status)
    if status[0] == BL_ACK:
        print("|    Erase Application Flash Successful" + " "*55 + "|")
    elif status[0] == BL_NACK:
        print("|    Erase Application Flash Failure" + " "*58 + "|")
    else:
        print("|    Received status is : " + str(status[0]) + " "*60 + "|")
    
elif user_ip == CMD_BOOTLOADER_FLASH_APPLI:
    transmit_data = My_Serial.word_to_bytelist(CMD_BOOTLOADER_FLASH_APPLI, My_Serial.hex_len(CMD_BOOTLOADER_FLASH_APPLI))
    crc_value = Crc_calc.calc_Crc32Mpeg2(transmit_data,len(transmit_data))
    crc_value = My_Serial.word_to_bytelist(crc_value, My_Serial.hex_len(crc_value) )
    for element in crc_value:
        transmit_data.append(element)
    #Transmit the command first    
    for byte in transmit_data:
        My_Serial.Write_to_serial_port(byte)
    
    #check the acknowledement
    status = My_Serial.get_ACK()
    process_bin()
    
elif user_ip == CMD_BOOTLOADER_JUMPTO_APPL:
    transmit_data = My_Serial.word_to_bytelist(CMD_BOOTLOADER_JUMPTO_APPL, My_Serial.hex_len(CMD_BOOTLOADER_JUMPTO_APPL))
    crc_value = Crc_calc.calc_Crc32Mpeg2(transmit_data,len(transmit_data))
    crc_value = My_Serial.word_to_bytelist(crc_value, My_Serial.hex_len(crc_value) )
    for element in crc_value:
        transmit_data.append(element)
    #Transmit the command first    
    for byte in transmit_data:
        My_Serial.Write_to_serial_port(byte)
    
    #check the acknowledement
    status = My_Serial.get_ACK()    
    

else:
    print("NO IMPLEMENTATION")
    

 
print("|" + "_"*93 + "|")



#END