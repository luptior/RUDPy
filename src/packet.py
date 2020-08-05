import datetime
import hashlib
import pickle
import socket
import threading
import time
import numpy as np
from reedsolo import RSCodec, ReedSolomonError

# Packet class definition
class packet:

    def __init__(self):
        self.rsc = RSCodec(10)  # default to be 10
        self.delimiter = b"|:|:|" # type bytes
        self.checksum = 0 # type String
        self.seqNo = 0
        self.msg = 0

    # return checksum as string
    def get_checksum(self) -> str:
        if isinstance(self.checksum, str):
            return self.checksum
        elif isinstance(self.checksum, bytes) or isinstance(self.checksum, bytearray):
            return self.checksum.decode("utf-8")


    # return seq as int
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

    def make(self, data, seq: int):
        self.seqNo = seq
        if isinstance(data, bytes):
            self.msg = data
            self.checksum = hashlib.sha1(self.msg).hexdigest()
        elif isinstance(data, str):
            self.msg = data.encode("utf-8")
            self.checksum = hashlib.sha1(self.msg).hexdigest()

    def tobytes(self) -> bytes:
        elements = [self.get_checksum(),
                    str(self.get_seq()),
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
        self.checksum, self.seqNo, self.msg = [x.decode().encode() for x in data]
        self.seqNo = str(self.seqNo)
        return


if __name__ == '__main__':
    pkt = packet()
    pkt2 = packet()
    data = np.random.randint(100, size = (2,3)).tobytes()

    pkt.make(data)

    print(data)
    print(pkt.serialize())
    pkt2.deserialize(pkt.serialize())
    print(pkt2.get_seq())
    print(pkt2.get_msg())