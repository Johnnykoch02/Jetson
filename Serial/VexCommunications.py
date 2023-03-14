import time
import serial
import json
import asyncio
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
    def __init__( self ):
        self.__callbacks = dict.fromkeys(range(0, 256))
        self.__stop_token = False
        self.__next_packet = [ 1 ]
        self.__packet_header = [ 115, 111, 117, 116 ]
        self.__end_of_transmission = [ 11, 11, 10, 0 ]
        self.header_length = len(self.__packet_header) + 1
        self.footer_length = len(self.__end_of_transmission)
        self.__FindPort()
        self.last_date = datetime.now()
        self.__callbacks[0] = CallbackItem("", self.RecieveTagList)

    def __FindPort( self ):
        ports = serial.tools.list_ports.comports()
        for port, desc, hwid in sorted(ports):
            if hwid.find("2888:0501") > 0 and hwid.find("LOCATION") > 0:
                print("Located at: {}".format(port))
                self.com = port
                break
        self.serial = serial.Serial(self.com)   

    def __FindCallbackItem( self, name ):
        first_none = 0
        for i in self.__callbacks:
            item = self.__callbacks[i]
            if item is not None:
                if item.friendly_name == name:
                    return i
            if item is None and first_none == 0:
                first_none = i
        return first_none
    
    def SendRawBuffer(bytes):
        pass

    def RecieveTagList( self, array ):
        print(array)

    def RegisterCallback( self, name, method ):
        index = self.__FindCallbackItem(name)
        self.__callbacks[index] = CallbackItem(name, method)
        return index

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
        item = self.__callbacks[packet[self.header_length]]
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