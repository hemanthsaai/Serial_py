#import necessary Modules
import serial
import sys
import glob
import struct
import os

#MACRO KIND INITIALIZATIONS
PASS = 1
FAIL = 0


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
    return byte_list
    
#Start Application Implementation here
def start_here():        
    open_port = open_serial_port()
    if open_port:
        open_port.close()
        byte_list = word_to_bytelist(0x12345678, 2)
        print(byte_list)


os.system("cls")        
global open_port
start_here()

