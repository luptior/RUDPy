import datetime
import hashlib
import pickle
import socket
import threading
import time
import numpy as np
from reedsolo import RSCodec, ReedSolomonError

from packet import Packet

# Packet class definition
class Packet:

    def __init__(self):
        self.rsc = RSCodec(10)  # default to be 10
        self.delimiter = b"|:|:|" # type bytes
        self.checksum = 0 # type String
        self.length = str(0)
        self.seqNo = 0
        self.msg = 0

    # return checksum as string
    def get_checksum(self) -> str:
        if isinstance(self.checksum, str):
            return self.checksum
        elif isinstance(self.checksum, bytes) or isinstance(self.checksum, bytearray):
            return self.checksum.decode("utf-8")

    # return length as int
    def get_length(self) -> int:
        if isinstance(self.length, int):
            return self.length
        elif isinstance(self.length, bytes) or isinstance(self.length, bytearray):
            return int(self.length.decode("utf-8"))
        elif isinstance(self.length, str):
            if "b'" in self.length:
                self.length = eval(self.length)
                return self.get_length()
            else:
                return int(self.length)

    # return length as int
    def get_seq(self) -> int:
        if isinstance(self.seqNo, int):
            return self.seqNo
        elif isinstance(self.seqNo, bytes) or isinstance(self.seqNo, bytearray):
            return int(self.seqNo.decode("utf-8"))
        elif isinstance(self.seqNo, str):
            if "b'" in self.seqNo:
                self.seqNo = eval(self.seqNo)
                return self.get_seq()
            else:
                return int(self.seqNo)

    def get_msg(self) -> bytes:
        if isinstance(self.msg, bytes):
            return self.msg
        elif isinstance(self.msg, bytearray):
            return self.msg.decode("utf-8").encode("utf-8")
        elif isinstance(self.msg, str):
            return self.msg.encode("utf-8")

    def make(self, data):
        if isinstance(data, bytes):
            self.msg = data
            self.length = str(len(data))
            self.checksum = hashlib.sha1(self.msg).hexdigest()
            print(f"Length: {self.length}\nSequence number: {self.seqNo}")
        elif isinstance(data, str):
            self.msg = data.encode("utf-8")
            self.length = str(len(data))
            self.checksum = hashlib.sha1(self.msg).hexdigest()
            print(f"Length: {self.length}\nSequence number: {self.seqNo}")

    def tobytes(self) -> bytes:
        elements = [self.get_checksum(),
                    str(self.get_seq()),
                    str(self.get_length()),
                    self.get_msg().decode('utf-8')]

        elements = [ x if isinstance(x, bytes) else x.encode('utf-8') for x in elements ]

        serialized_packet = self.delimiter.join(elements)
        return serialized_packet

    def serialize(self) -> bytes:
        # encode the whole object string to bytes
        # then add RS coding
        return self.rsc.encode(self.tobytes())

    def deserialize(self, input: bytearray):
        data = self.rsc.decode(input)[0].split(self.delimiter)
        self.checksum, self.length, self.seqNo, self.msg = [x.decode().encode() for x in data]
        self.length = str(self.length)
        self.seqNo = str(self.seqNo)
        return


