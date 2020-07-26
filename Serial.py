#import necessary Modules
import serial
import sys
import glob
import struct
import os
import Crc_calc

#MACRO KIND INITIALIZATIONS
PASS                            = 1
FAIL                            = 0
COM_ACK                         = 0xA5
COM_NACK                        = 0xA6
      
global open_port

# Scan and returns a list of open COM ports 
def Identify_Open_COM_PORTS():
    if sys.platform.startswith('win'):
        port_list = ['COM%s' %(i+1) for i in range(256)]
    elif sys.platform.startswith('cygwin') or sys.platform.startswith('linux'):
        ports = glob.glob('/dev/tty[A-Za-z]*')
    else:
        print("IMPLEMENTATION ONLY FOR WINDOWS")
          
    result = []
    for port in port_list:
        try:
            sts = serial.Serial(port)
            sts.close()
            result.append(port)
        except:
            pass
    return result

#From available COM ports it takes input from USER
#and connects to the serial port.
#Once the connection is ready it returns the PORT as it is.
#USAGE:  open_port = open_serial_port()
#       if (open_port):
#           open_port.readline()
def open_serial_port():   

    port_list = Identify_Open_COM_PORTS()
    if port_list:
        print("OPEN COM PORTS AVAILABLE :")
    else:
        print("No COM ports are available to open.")
        return FAIL
        
    count = 1
    for port in port_list:
        print(str(count) +  ".   "   + port)
    selected_port = int(input("Select the port input 1 or 2 ... :"))
    
    if selected_port > count:
        print("Invalid COM PORT selected. Please try again !!!")
        return FAIL
    else:
        try:
            open_port = serial.Serial(port_list[selected_port-1],115200,timeout=3)
        except:
            print("Error in opening PORT " + port_list[selected_port-1] + " Please check...")
            return FAIL
            
    if(open_port):
        print("PORT " + port_list[selected_port-1] + " OPENED SUCCESSFUL\n")
        return open_port
    else:
        print("Error in opening PORT " + port_list[selected_port-1] + " Please check...")
        return FAIL


#Writes ONE BYTE data (0x00..0xFF) to opened COM PORT 
#and returns the status of operation
#USAGE:   status = Write_to_serial_port(0x1)
def Write_to_serial_port(value):
    data = struct.pack('>B', value)
    print(data)
    value = bytearray(data)
    #print("   "+hex(value[0]), end='')
    print("   "+"0x{:02x}".format(value[0]),end=' ')
    try:
        open_port.write(data)
        return PASS
    except:
        print("Error in writing to PORT")
        return FAIL
        
#Reads "length" number of bytes specified via function argument
#and returns the data     
def Read_from_serial_port(length):
    if open_port:
        data = open_port.read(length)
        return data
  
#converts a 32 bit word to 8 bit
#retuns a list of bytes   
#USAGE: byte_list = word_to_bytelist(0x12345678, 2)
#  o/p :  [0x78,0x56]
def word_to_bytelist(word,length):
    byte_list = []
    for i in range(length):
        byte_list.append(    ( (word >> (8 * i))  & 0x000000FF )     )
    byte_list.reverse()
    return byte_list
    
#returns number of bytes in the given number 
def hex_len(data):
    length = len(hex(data))-2
    length = int(length)
    if int(length%2):
        return int((length+1)/2)     # if len is 3 then the number of bytes is 1.5(0xFFF), so round it off to 2 bytes
    else:
        return int(length/2)     
        
        
#reads one byte from COM PORT and verifies if the 
#byte is ACK-0xA5 or NACK        
def get_ACK():
    rx_ack = 0
    while rx_ack == 0:    
        rx_ack = open_port.read(1)    
    print("\n")
    print(rx_ack)
    if rx_ack[0]    == COM_ACK:
        print("AcK receeived correctly")
        return PASS
    else:
        print("Invalid Ack received")
        return FAIL
        
        
        
    
#Start Application Implementation here
#def start_here():        
open_port = open_serial_port()
if open_port:
    delay = int(input("Enter Required Delay:"))
    to_transmit = []
    
    #transmit length 
    to_transmit = word_to_bytelist(hex_len(delay), 1)
    crc_val = Crc_calc.calc_Crc32Mpeg2(to_transmit,len(to_transmit))
    print(crc_val)
    crc_val_to_transmit = word_to_bytelist(  crc_val, hex_len(crc_val) )
    print(crc_val_to_transmit)
    for element in crc_val_to_transmit:
        to_transmit.append(element)
        
    print(to_transmit)
    for byte in to_transmit:
        Write_to_serial_port(byte)
    
    get_ACK()
        
    to_transmit = []
    #transmit delay
    delay_to_transmit = word_to_bytelist(  delay, hex_len(delay) )
    print(delay_to_transmit)
    for element in delay_to_transmit:
        to_transmit.append(element)
    
    crc_val = Crc_calc.calc_Crc32Mpeg2(to_transmit,len(to_transmit))
    print(crc_val)
    crc_val_to_transmit = word_to_bytelist(  crc_val, hex_len(crc_val) )
    print(crc_val_to_transmit)
    for element in crc_val_to_transmit:
        to_transmit.append(element)
               
    print(to_transmit)
        
    for byte in to_transmit:
        Write_to_serial_port(byte)
        
    get_ACK()    
        
        
    open_port.close()
        
        



#os.system("cls")  
#start_here()

