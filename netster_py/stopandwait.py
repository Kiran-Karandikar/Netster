# Standard Library
from socket import AF_INET, SOCK_DGRAM, socket, timeout
from struct import pack
from typing import BinaryIO


class IncorrectSequenceNumber(Exception):
    pass


def stopandwait_server(iface: str, port: int, fp: BinaryIO) -> None:
    last_seen_header = None
    with socket(AF_INET, SOCK_DGRAM) as a_socket:
        a_socket.bind((iface, port))

        print("Hello, I am a Server")
        while True:
            packet, (host, port) = a_socket.recvfrom(258)
            header = packet[:2]

            # check for what header we are receiving.
            if last_seen_header is None or last_seen_header != header:
                last_seen_header = header

                # send acknowledgement to client
                a_socket.sendto(last_seen_header, (host, port))

                data = packet[2:]
                if len(data) == 0:
                    break
                else:
                    fp.write(data)
            else:
                a_socket.sendto(last_seen_header, (host, port))

    fp.close()


def stopandwait_client(host: str, port: int, fp: BinaryIO) -> None:
    message_size = 256
    sequence_number = 0

    with socket(AF_INET, SOCK_DGRAM) as a_socket:
        print("Hello, I am a client")

        a_socket.settimeout(0.06)
        while True:
            next_packet = False
            sequence_number = int(not sequence_number)
            # Some of the below code is adapted from the python documentation on struct
            # source: https://docs.python.org/3/library/struct.html#module-struct
            # source: https://docs.python.org/3/library/struct.html#format-characters

            # begin snippet
            rudp_header = pack("!h", sequence_number)
            # end snippet

            data = fp.read(message_size)
            packet = rudp_header + data if len(data) != 0 else rudp_header + b""
            a_socket.sendto(packet, (host, port))

            while not next_packet:
                try:
                    sq_number, (host, port) = a_socket.recvfrom(2)
                    if rudp_header != sq_number:
                        raise IncorrectSequenceNumber()
                    next_packet = True

                except (timeout, IncorrectSequenceNumber):
                    a_socket.sendto(packet, (host, port))

            # after acknowledgement of empty data.
            if len(data) == 0:
                break
    fp.close()
