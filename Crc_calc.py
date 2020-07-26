import      struct
from        crccheck.crc import Crc32Mpeg2

#-----------------------------------------------------------------------------------------------------
#References for calc_Crc32Mpeg2:
#-----------------------------------------------------------------------------------------------------
#https://pypi.org/project/crccheck/
#https://pythonhosted.org/crccheck/_modules/crccheck/crc.html#Crc32Mpeg2
#https://stackoverflow.com/questions/17534345/typeerror-missing-1-required-positional-argument-self
#https://crccalc.com/
#-----------------------------------------------------------------------------------------------------
#Calculates Crc32Mpeg2 value of the given list and its length
#returns a int value of calculated CRC
def calc_Crc32Mpeg2(data,length):
    crcinst = Crc32Mpeg2()
    for i in range(length):
        value = struct.pack('>B', data[i])
        crcinst.process(value)
        length = length-1
        
    return crcinst.final()