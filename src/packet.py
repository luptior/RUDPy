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
        self.title = 0
        self.msg = 0

    # return checksum as string
    def get_checksum(self) -> str:
        if isinstance(self.checksum, str):
            return self.checksum
        elif isinstance(self.checksum, bytes) or isinstance(self.checksum, bytearray):
            return self.checksum.decode("utf-8")

    def get_title(self) -> bytes:
        if isinstance(self.title, bytes):
            return self.title
        elif isinstance(self.title, bytearray):
            return self.title.decode("utf-8").encode("utf-8")
        elif isinstance(self.title, str):
            return self.title.encode("utf-8")

    # return seq as int
    # title should be in format title_seq
    def get_seq(self) -> int:
        try:
            return int(self.get_title().decode().split("_")[-1])
        except ValueError:
            print(self.get_title().decode())

    def get_msg(self) -> bytes:
        if isinstance(self.msg, bytes):
            return self.msg
        elif isinstance(self.msg, bytearray):
            return self.msg.decode("utf-8").encode("utf-8")
        elif isinstance(self.msg, str):
            return self.msg.encode("utf-8")

    def make(self, title: str, data):
        self.title = title
        if isinstance(data, bytes):
            self.msg = data
            self.checksum = hashlib.sha1(self.msg).hexdigest()
        elif isinstance(data, str):
            self.msg = data.encode("utf-8")
            self.checksum = hashlib.sha1(self.msg).hexdigest()

    def tobytes(self) -> bytes:
        elements = [self.get_checksum(),
                    self.get_title(),
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
        self.checksum, self.title, self.msg = [x.decode().encode() for x in data]
        return


if __name__ == '__main__':
    pkt = packet()
    pkt2 = packet()
    data = np.random.randint(100, size = (2,3)).tobytes()

    pkt.make("util_data_0", data)

    print(data)
    print(pkt.serialize())
    pkt2.deserialize(pkt.serialize())
    print(pkt2.get_seq())
    print(pkt2.get_msg())