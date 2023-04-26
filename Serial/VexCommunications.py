import time
import serial
import json
import asyncio
import threading
import struct
import serial.tools.list_ports
from datetime import datetime
from math import log10, floor

# [plen]sout[data][NL][0]

class FloatDeserializer:
    @staticmethod
    def Deserialize(array, length):
        length = array[0] - 10
        number = 0
        decimal = 0
        decimal_length = 0
        switch_to_decimal = False

        for i in range(1, length+1):
            if not switch_to_decimal:
                if array[i] != 7:
                    number *= 10
                    k = array[i] - 11
                    number += k
                    if k > 10 and i < length and array[i+1] - 11 > 10:
                        number *= 10
                else:
                    switch_to_decimal = not switch_to_decimal
            else:
                if array[i] != 7:
                    k = array[i] - 11
                    p = len(str(k))
                    decimal *= pow(10, p)
                    decimal += k
                    decimal_length += p
                else:
                    switch_to_decimal = not switch_to_decimal

        print("decimal:", decimal)
        divisor = pow(10, decimal_length)
        number += decimal / divisor

        return Deserializer(number, length+1)

class IntDeserializer: 
    @staticmethod
    def Deserialize(array, length) -> int:
        deserialized = FloatDeserializer.Deserialize(array, length)
        deserialized.value = int(deserialized.value)
        return deserialized

class NumberDeserializer:
    @staticmethod
    def Deserialize(array):
        length = array[0] - 10
        if 7 in array[1:length + 1]:
            return FloatDeserializer.Deserialize(array, length)
        else:
            return IntDeserializer.Deserialize(array, length)

class StringDeserializer:
    def Deserialize(array):
        length = ((array[0] << 8) + array[1]) - 10
        string = ''.join([chr(i) for i in array[2:length]])
        return Deserializer(string,length)

class Deserializer:

    def __init__( self, value, next: int ):
        self.value = value
        self.next = next

    def FindDeserializer( byte: int ):
        if byte == 1:
            return NumberDeserializer
        if byte == 2:
            return StringDeserializer
        
class CallbackItem:
    def __init__( self, name="", callback=None ):
        self.friendly_name = name
        self.callback = callback

class Communications:
    __callbacks = [None] * 256
    __extendedTags = [None] * 256
    __packetIndexOffset = 15
    __stop_token = False
    __next_packet = [ 1 ]
    __packet_header = [ 115, 111, 117, 116 ]
    __end_of_transmission = [ 0, 0, 10, 10 ]
    __recieved_tags = False
    header_length = len(__packet_header) + 1
    footer_length = len(__end_of_transmission)
        
    def __init__( self ):
        self.__recieved_tags = True
        self.__callbacks = [None] * 256
        self.__extendedTags = [None] * 256
        self.managed_thread = asyncio.new_event_loop()

    def __FindPort( self ):
        ports = serial.tools.list_ports.comports()
        for port, desc, hwid in sorted(ports):
            if hwid.find("2888:0501") > 0 and hwid.find("LOCATION") > 0:
                print("Located at: {}".format(port))
                self.com = port
                break
        self.serial = serial.Serial(self.com, \
            baudrate=128000,\
            parity=serial.PARITY_NONE,\
            stopbits=serial.STOPBITS_ONE,\
            bytesize=serial.EIGHTBITS,\
            timeout=0)

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
        ff = str(int(f)) if f == int(f) else str(f)
        
        stream = ""
        
        c = 0
        while c < len(ff):
            char_value = ord(ff[c])

            if 48 <= char_value <= 57:
                if c + 1 < len(ff) and 48 <= ord(ff[c + 1]) <= 57:
                    nchar = ((char_value - 48) * 10) + (ord(ff[c + 1]) - 37)
                    stream += chr(nchar)
                    c += 1
                else:
                    stream += chr(char_value - 37)
            elif char_value == 46:
                stream += chr(7)

            c += 1

        ret = chr(len(stream) + 10) + stream
        ret = chr(1) + ret

        return ret

    def SendPacket( self, name: str, *args) -> int:
        index = self.GetFunctionIndex(name, True)
        # print("Calling " + name + ": " + str(index))
        return self.InternalSendPacket(index, *args)

    def InternalSendPacket( self, index: int, *args) -> int:
        if index == None: return False
        buffer = chr(index)
        for arg in args:
            argType = type(arg).__name__
            if argType == "str":
                buffer += self.__SerializeString(arg)
            if argType == "int" or argType == "float":
                buffer += self.__SerializeNumber(arg)

        return self.SendRawBuffer(buffer)

    def GetFunctionIndex( self, name: str, required: bool = False) -> int:
        ind = self.__FindCallbackItem(name, required)
        if ind >= 0:
            return ind + self.__packetIndexOffset
        else:
            return None

    def SendRawBuffer( self, _bytes: str ) -> int:
        buffer = ""
        for num in self.__packet_header:
            buffer += chr(num)

        buffer += _bytes

        for num in self.__end_of_transmission:
            buffer += chr(num)
        
        buffer = chr(len(buffer)) + buffer

        # bb= ""
        # for b in buffer:
        #     bb += str(ord(b))+","
        # print(bb)

        return self.serial.write(bytes(buffer, encoding="UTF8"))

    def WaitForTags(self):
        self.__recieved_tags = False
        ctr = 0
        while(self.__recieved_tags == False):
            ctr+=1
            if ctr % 100 == 0:
                print('Watining for tags...')
            time.sleep(0.1)

    def __SendTags( self ):
        for i in range(0, len(self.__extendedTags)):
            item = self.__extendedTags[i]
            if item is not None:
                step = 1
                if (self.__extendedTags[i+1] is None): step = 0
                print("Sending Tag Update:", i, item.friendly_name)
                self.InternalSendPacket(1, step, i, item.friendly_name)
                if step == 0:
                    break

        self.__callbacks = self.__extendedTags
        self.__extendedTags = [None] * 256

    def RecieveTagList( self, array: list ):
        step = array[0]
        tag_id = array[1]
        friendly_name = array[2]
        self.__extendedTags[tag_id] = CallbackItem(friendly_name, None)
        found_callback = [i for i in self.__callbacks if i is not None and i.friendly_name == friendly_name]
        if found_callback:
            self.__extendedTags[tag_id].callback = found_callback[0].callback
            
        
        print("Recieved: " + friendly_name)

        if (step == 0):
            itr = 0
            for y in range(len(self.__extendedTags)):
                if self.__extendedTags[y] == None and self.__callbacks[itr] != None:
                    self.__extendedTags[y] = self.__callbacks[itr]
                    itr+=1
            self.__SendTags()
            self.__recieved_tags = True
        else:
            self.__recieved_tags = False

    def RegisterCallback( self, name: str, method ):
        index = self.__FindCallbackItem(name)
        print("Registered:", index, name)
        self.__callbacks[index] = CallbackItem(name, method)
    
    def HasCallback( self, name: str ) -> bool:
        for idx, _callback in self.__callbacks.items():
            if _callback.friendly_name == name:
                return True
        return False
    
    async def __ReadInput( self ):
        self.__FindPort()
        self.last_date = datetime.now()
        print("Communications Open")
        while not self.__stop_token:
            #self.serial.write(10)
            for _int in self.serial.read():
                # print(_int)
                packet_length = len(self.__next_packet)
                #if packet_length - 1 < self.__next_packet[0]:
                if packet_length >= self.header_length:
                    self.__next_packet.append(_int)
                    if self.__next_packet[-self.footer_length:] == self.__end_of_transmission:
                        if len(self.__next_packet) > self.footer_length + self.header_length:
                            #self.last_date = datetime.now()
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
            if self.__recieved_tags == False:
                item = CallbackItem("__Reserved_RecieveTagList", self.RecieveTagList)
            else:
                return
        else:
            item = self.__callbacks[function_id - self.__packetIndexOffset]
        
        print(function_id - self.__packetIndexOffset)
        print([i.friendly_name for i in self.__callbacks if i is not None])
        
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
        print("Parse Time: {}".format(diff.total_seconds() * 1000000))
        item.callback(paramaters)

    def __run_coroutine(self):
        asyncio.set_event_loop(self.managed_thread)
        self.managed_thread.run_until_complete(self.__ReadInput())

    def Start( self ):
        threading.Thread(target=self.__run_coroutine).start()