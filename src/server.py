"""
server reads file and send to client

"""

import datetime
import pickle
import socket
import threading
import time
import numpy as np
from packet import packet


# Connection handler
def sending_data(data, addr, fragment_size=500):
    drop_count = 0
    packet_count = 0

    if lossSimualation:
        packet_loss_percentage = float(input("Set PLP (0-99)%: ")) / 100.0
        while packet_loss_percentage < 0 or packet_loss_percentage >= 1:
            packet_loss_percentage = float(input("Enter a valid PLP value. Set PLP (0-99)%: ")) / 100.0
    else:
        packet_loss_percentage = 0

    print("Request started at: " + str(datetime.datetime.utcnow()))
    pkt = packet()
    threadSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    seqs = [x for x in range(len(data)//fragment_size+1)]
    partial_msgs = [ data[x * fragment_size: (x + 1) * fragment_size] for x in seqs]

    for counter in seqs:

        title = f"util_msg_{counter}"
        print(f"Sending package {title}")
        packet_count += 1
        randomised_plp = np.random.random()
        if packet_loss_percentage < randomised_plp:

            # extract the partial dat to be msg
            msg = partial_msgs[counter]
            pkt.make(title, msg)
            serialized_pkt = pkt.serialize()

            # Send packet
            threadSock.sendto(serialized_pkt, addr)
            print(f'Sent to {addr}, awaiting acknowledgment..')
            # threadSock.settimeout(10)

            # Wait for Ack
            try:
                ack, _ = threadSock.recvfrom(100)
                ack = pickle.loads(ack)
            except socket.timeout:
                print("Time out reached, resending ...%s" % counter)
                continue
            if ack.split(",")[0] == str(pkt.get_seq()):
                print(f"Acknowledged by: {ack} \n")
        else:
            print("Dropped packet\n")
            drop_count += 1

    print(f"packets served: {packet_count}")

    if lossSimualation:
        print(f"Dropped packets:  {str(drop_count)} "
              f"\nComputed drop rate: {float(drop_count) / float(packet_count) * 100.0}")

    print("Sending finished.")





if __name__ == '__main__':
    # PLP Simulation settings
    lossSimualation = False

    # Set addr and port
    IP = "localhost"
    server_port = 8233
    client_port = 10500

    # Seq number flag
    seqFlag = 0

    # Start - Connection initiation
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Bind the socket to the port
    server_address = (IP, server_port)
    print('Starting up on %s port %s' % server_address)
    sock.bind(server_address)

    data = np.random.randint(100, size=[5, 6, 5]).tobytes()
    sending_data(data, (IP, client_port))

    # print('Waiting to receive message')
    # pdata, address = sock.recvfrom(600)
    # connectionThread = threading.Thread(target=sending_data, args=((IP, client_port),))
    # connectionThread.start()
    # print('Received %s bytes from %s' % (len(pdata), address))
