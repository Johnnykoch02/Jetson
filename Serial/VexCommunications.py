import time
import serial
import json
import asyncio
import struct
import serial.tools.list_ports
from datetime import datetime

# [plen]sout[data][NL][0]

class FloatDeserializer:
    def Deserialize(array, length):
        number = 0
        decimal = 0
        switch = False
        for i in range(1, length):
            if array[i] == 7:
                switch = True
                continue
            if not switch:
                number *= 10
                number += (array[i] - 11)
            else:
                decimal *= 10
                decimal += (array[i] - 11)
        number = float(str(number)+"."+str(decimal))
        return Deserializer(number, length)

class IntDeserializer: 
    def Deserialize(array, length):
        number = 0
        for i in range(1, length):
            number *= 10
            number += (array[i] - 11)
        return Deserializer(number, length)

class NumberDeserializer:
    def Deserialize(array):
        length = array[0] - 9
        if 7 in array[1:length]:
            return FloatDeserializer.Deserialize(array, length)
        else:
            return IntDeserializer.Deserialize(array, length)
    
class StringDeserializer:
    def Deserialize(array):
        length = (array[0] - array[1]) - 11
        print(length)
        string = array[2:length]
        print(string)
        return Deserializer(0,0)

class Deserializer:

    def __init__( self, value, next ):
        self.value = value
        self.next = next

    def FindDeserializer( byte ):
        if byte == 1:
            return NumberDeserializer
        if byte == 2:
            return StringDeserializer
        
class CallbackItem:
    friendly_name = ""
    callback = None
    def __init__( self, name, callback ):
        self.friendly_name = name
        self.callback = callback

class Communications:
    __callbacks = list[CallbackItem]()
    __extendedTags = list[CallbackItem]()
    __packetIndexOffset = 15
    __stop_token = False
    __next_packet = [ 1 ]
    __packet_header = [ 115, 111, 117, 116 ]
    __end_of_transmission = [ 11, 11, 10, 0 ]
    __recieved_tags = False
    header_length = len(__packet_header) + 1
    footer_length = len(__end_of_transmission)
    
    def __init__( self ):
        self.__recieved_tags = False
        self.__callbacks = list[CallbackItem]() * 256
        self.__extendedTags = list[CallbackItem]() * 256
        self.__FindPort()
        self.last_date = datetime.now()

    def __FindPort( self ):
        ports = serial.tools.list_ports.comports()
        for port, desc, hwid in sorted(ports):
            if hwid.find("2888:0501") > 0 and hwid.find("LOCATION") > 0:
                print("Located at: {}".format(port))
                self.com = port
                break
        self.serial = serial.Serial(self.com)   

    def __FindCallbackItem( self, name: str, require_find: bool = False ):
        for i in range(len(self.__callbacks)):
            item = self.__callbacks[i]
            if item is not None:
                if item.friendly_name == name:
                    return i
            elif not require_find:
                return i
        return -1
    
    def __SerializeString(self, s: str) -> str:
        stream = chr(2)
        string_length = struct.pack('>H', len(s) + 10)
        stream += chr(string_length[0]) + chr(string_length[1])
        stream += s
        return stream

    def __SerializeNumber(self, f: float) -> str:
        stream = ""
        ff = ""

        if f == int(f):
            ff = str(int(f))
        else:
            ff = str(f)

        for c in range(len(ff)):
            chr_ = ord(ff[c])

            if 48 <= chr_ <= 57:
                if c + 1 < len(ff) and 48 <= ord(ff[c+1]) <= 57:
                    nchar = ((chr_ - 48) * 10) + (ord(ff[c+1]) - 37)
                    stream += chr(nchar)
                    c += 1
                else:
                    stream += chr(chr_ - 37)
            elif chr_ == 46:
                stream += chr(7)

        ret = chr(len(stream) + 10) + stream
        ret = chr(1) + ret
        return ret

    def SendPacket( self, name: str, *args) -> bool:
        index = self.GetFunctionIndex(name)
        return self.SendPacket(index, args)

    def SendPacket( self, index: int, *args) -> bool:
        buffer = ""
        
        if index == None: return False
        buffer += chr(index)
        
        for arg in args:
            argType = str(type(arg))
            if argType == "String":
                buffer += self.__SerializeString(arg)
            if argType == "Float":
                buffer += self.__SerializeNumber(arg)
        
        for num in self.__end_of_transmission:
            buffer += chr(num)
        
        buffer = chr(len(buffer)) + buffer
        True

    def GetFunctionIndex( self, name: str) -> int:
        ind = self.__FindCallbackItem(name)
        if ind >= 0:
            return ind + self.__packetIndexOffset
        else:
            return None

    def SendRawBuffer(bytes):
        pass

    def WaitForTags(self):
        while(self.__recieved_tags == False):
            pass

    def __SendTags( self ):
        for i in range(len(self.__callbacks)):
            item = self.__callbacks[i]
            step = 0
            if (self.__callbacks[i+1] is None):
                step = 1
            self.SendPacket(0, 0, step, item.friendly_name)
            if step == 1: return

    def RecieveTagList( self, array: list ):
        step = array[0]
        tag_id = array[1]
        friendly_name = array[2]
        self.__extendedTags[tag_id] = CallbackItem(friendly_name)
        
        if (step == 0):
            self.__callbacks = self.__extendedTags.extend(self.__callbacks)
            self.__extendedTags = list[CallbackItem] * 256
            self.__recieved_tags = True
            self.__SendTags()
        else:
            self.__recieved_tags = False

    def RegisterCallback( self, name: str, method: function ):
        index = self.__FindCallbackItem(name)
        self.__callbacks[index] = CallbackItem(name, method)

    def __ReadInput( self ):
        print("Communications Open")
        while not self.__stop_token:
            for _int in self.serial.read():
                packet_length = len(self.__next_packet)
                if packet_length - 1 < self.__next_packet[0]:
                    if packet_length >= self.header_length:
                        self.__next_packet.append(_int)
                        if self.__next_packet[-self.footer_length:] == self.__end_of_transmission:
                            self.__ParsePacket(self.__next_packet)
                            self.__next_packet = [ 1 ]
                        continue
                    elif _int == self.__packet_header[packet_length-1]:
                        self.__next_packet.append(_int)
                        continue
                self.__next_packet = [ _int ]

    def __ParsePacket( self, packet ):
        function_id = packet[self.header_length]
        if function_id == 1:
            item = CallbackItem("__Reserved_RecieveTagList", self.RecieveTagList)
        else:
            item = self.__callbacks[function_id - self.__packetIndexOffset]
        
        print("================================")
        print("Function Called: \"{}\"".format(item.friendly_name))   
        print("Total Bytes: {}".format(len(packet)))
        
        packet = packet[self.header_length:-self.footer_length]
        pindex = 1
        paramaters = []
        
        while pindex < len(packet):
            deserializer = Deserializer.FindDeserializer(packet[pindex])
            data = deserializer.Deserialize(packet[pindex+1:])
            paramaters.append(data.value)
            pindex += data.next + 1
        
        print("Parameters: {}".format(paramaters))
        diff = (datetime.now() - self.last_date)
        self.last_date = datetime.now()
        
        print("Time Since Last Call: {}".format(diff.total_seconds()))
        item.callback(paramaters)

    def Start( self ):
        self.read_loop = asyncio.create_task (self.__ReadInput())