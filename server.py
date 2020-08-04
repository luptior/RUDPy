"""
server reads file and send to client

"""

import datetime
import hashlib
import pickle
import socket
import threading
import time
import numpy as np
from reedsolo import RSCodec, ReedSolomonError


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


# Connection handler
def handleConnection(addr, ):
    drop_count = 0
    packet_count = 0
    fragment_size = 500
    time.sleep(0.5)
    if lossSimualation:
        packet_loss_percentage = float(input("Set PLP (0-99)%: ")) / 100.0
        while packet_loss_percentage < 0 or packet_loss_percentage >= 1:
            packet_loss_percentage = float(input("Enter a valid PLP value. Set PLP (0-99)%: ")) / 100.0
    else:
        packet_loss_percentage = 0

    print("Request started at: " + str(datetime.datetime.utcnow()))
    pkt = Packet()
    threadSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    data = np.random.randint(100, size=[3, 4]).tobytes()

    # Fragment and send file fragment_size byte
    x = 0
    while x < int(len(data) / fragment_size) + 1:
        print(f"Sending package {x}")
        packet_count += 1
        randomised_plp = np.random.random()
        if packet_loss_percentage < randomised_plp:

            # extract the partial dat to be msg
            msg = data[x * fragment_size: (x + 1) * fragment_size]
            pkt.make(msg)
            serialized_pkt = pkt.serialize()

            # Send Packet
            sent = threadSock.sendto(serialized_pkt, addr)
            print(f'Sent {sent} bytes back to {addr}, awaiting acknowledgment..')
            threadSock.settimeout(10)

            # Wait for Ack
            try:
                ack, addr = threadSock.recvfrom(100)
                ack = pickle.loads(ack)
            except:
                print("Time out reached, resending ...%s" % x)
                continue
            if ack.split(",")[0] == str(pkt.seqNo):
                pkt.seqNo = int(not pkt.seqNo)
                print(f"Acknowledged by: {ack} ")
                x += 1
        else:
            print("Dropped Packet\n")
            drop_count += 1

    print(f"Packets served: {packet_count}")

    if lossSimualation:
        print(f"Dropped packets:  {str(drop_count)} "
              f"\nComputed drop rate: {float(drop_count) / float(packet_count) * 100.0}")

    print("Sending finished.")


if __name__ == '__main__':
    # PLP Simulation settings
    lossSimualation = False

    # Set addr and port
    serverAddress = "localhost"
    serverPort = 8233

    # Seq number flag
    seqFlag = 0

    # Start - Connection initiation
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Bind the socket to the port
    server_address = (serverAddress, serverPort)
    print('Starting up on %s port %s' % server_address)
    sock.bind(server_address)

    # Listening for requests indefinitely

    print('Waiting to receive message')
    pdata, address = sock.recvfrom(600)
    connectionThread = threading.Thread(target=handleConnection, args=(address,))
    connectionThread.start()
    print('Received %s bytes from %s' % (len(pdata), address))
