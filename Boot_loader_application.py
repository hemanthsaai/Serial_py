import Crc_calc
import My_Serial
import struct
import os
import sys

#MACRO DEFINITIONS
CMD_BOOTLOADER_GET_VERSION      = 0xB1      #get Bootloader Version
CMD_BOOTLOADER_GET_CHIP_ID      = 0xB2      #get chip identification number
CMD_BOOTLOADER_ERASE_APPLI      = 0xB3      #erase Application
CMD_BOOTLOADER_FLASH_APPLI      = 0xB4      #flash Application
CMD_BOOTLOADER_INTEG_CHECK      = 0xB5      #check Integrity

TXT_BOOTLOADER_GET_VERSION      = "CMD_BOOTLOADER_GET_VERSION"
TXT_BOOTLOADER_GET_CHIP_ID      = "CMD_BOOTLOADER_GET_CHIP_ID"
TXT_BOOTLOADER_ERASE_APPLI      = "CMD_BOOTLOADER_ERASE_APPLI"
TXT_BOOTLOADER_FLASH_APPLI      = "CMD_BOOTLOADER_FLASH_APPLI"
TXT_BOOTLOADER_INTEG_CHECK      = "CMD_BOOTLOADER_INTEG_CHECK"

LEN_BOOTLOADER_GET_VERSION      = 0x1
LEN_BOOTLOADER_GET_CHIP_ID      = 0x4
LEN_BOOTLOADER_ERASE_APPLI      = 0x2
LEN_BOOTLOADER_FLASH_APPLI      = 0x1
LEN_BOOTLOADER_INTEG_CHECK      = 0x1

PASS                            = 0x1
FAIL                            = 0x0


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
    print("|" + "_"*93 + "|")
    user_ip = int(input("|    Provide Input : ")) + 0xB0
    print("|" + "_"*93 + "|")
    return PASS

    
menu_list()

transmit_data = []
if user_ip == CMD_BOOTLOADER_GET_VERSION:
    transmit_data = My_Serial.word_to_bytelist(CMD_BOOTLOADER_GET_VERSION, My_Serial.hex_len(CMD_BOOTLOADER_GET_VERSION))
    crc_value = Crc_calc.calc_Crc32Mpeg2(transmit_data,len(transmit_data))
    crc_value = My_Serial.word_to_bytelist(crc_value, My_Serial.hex_len(crc_value) )
    for element in crc_value:
        transmit_data.append(element)
        
    for byte in transmit_data:
        My_Serial.Write_to_serial_port(byte)
        
    status = My_Serial.get_ACK()

    ver = My_Serial.Read_from_serial_port(LEN_BOOTLOADER_GET_VERSION)
    print("|    Boot Loader Version Number : " + str(int(ver[0])) + " "*58 + "|")
    
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
    
else:
    print("NO IMPLEMENTATION")
    
    
print("|" + "_"*93 + "|")



