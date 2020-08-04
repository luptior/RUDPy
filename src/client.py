"""
client request data

"""

import socket
import hashlib
import pickle
import numpy as np

from src.packet import packet

## some constants

# Set addr and port
server_address = "localhost"
server_port = 8233
fragment_size = 500

# Delimiter
delimiter = "|:|:|"

if __name__ == '__main__':

    data_store = b""

    # Start - Connection initiation

    # while True:  # infinite loop if no exit signal
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(10)

    # no actual meaning just tell the sender starts sending message

    try:
        # Connection trials
        connection_trials_count = 0

        # Send first message to request sending
        print(f'Requesting')
        pdata = pickle.dumps("init")
        sent = sock.sendto(pdata, (server_address, server_port))
        print(f'Sent initial request')

        # Receive indefinitely
        while 1:
            # Receive response
            # print('\nWaiting to receive..')
            try:
                pdata, server = sock.recvfrom(4096)
                # Reset failed trials on successful transmission
                connection_trials_count = 0
            except: # TODO: better catch
                # retrying part
                connection_trials_count += 1
                if connection_trials_count < 5:  # arbitrarily set to 5, can be adaptive
                    print("\nConnection time out, retrying")
                    continue
                else:
                    print("\nMaximum connection trials reached, skipping request\n")
                    # os.remove("r_" + userInput)
                    break

            pkt = packet()
            pkt.deserialize(pdata)

            clientHash = hashlib.sha1(pkt.get_msg()).hexdigest()

            if pkt.get_checksum() == clientHash:

                data_store += pkt.get_msg()

                print(f"Sequence number: {pkt.get_seq()} Length: {pkt.get_length()}")
                # print(f"Server: %s on port {server}")

                # send ack to sender
                ack_deq_no = f"{pkt.get_seq()},{pkt.get_length()}"
                sent = sock.sendto(pickle.dumps(ack_deq_no), server)
                print(f'Sent ack for {pkt.get_seq()}')
            else:
                print("Checksum mismatch detected, dropping packet")
                print("Server hash: " + pkt.get_checksum() + " Client hash: " + clientHash)
                print(f"Server: %s on port {server}")
                continue

            if pkt.get_length() < fragment_size:
                pkt.seqNo = int(not pkt.get_length())
                break

    finally:
        print("Closing socket")
        sock.close()
        print(np.frombuffer(data_store, int).reshape(5,6,5))
