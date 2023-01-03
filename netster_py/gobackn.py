# Standard Library
from collections import deque
from datetime import datetime, timedelta
from socket import AF_INET, SOCK_DGRAM, socket, timeout
from struct import pack
from typing import BinaryIO


# Global Vars
DEFAULT_TIMEOUT = 0.06
MESSAGE_SIZE = 256


class RUDPPacket:
    def __init__(self, **kwargs):
        self.sq_number = kwargs.get("sequence_number")
        self.data = kwargs.get("data", None)
        # Some of the below code is adapted from the python documentation on struct
        # source: https://docs.python.org/3/library/struct.html#module-struct
        # source: https://docs.python.org/3/library/struct.html#format-characters

        # begin snippet
        self.header = pack("!h", self.sq_number)
        # end snippet

        self.packet = None
        self.send_time = None
        self.expiry = None
        self.timeout = None

    def generate_timeouts(self, previous_packet_send_time=None):
        # Generate packet timeouts based upon the current system time and previous packet in window.
        self.send_time = datetime.now()
        self.expiry = self.send_time + timedelta(seconds=DEFAULT_TIMEOUT)
        if previous_packet_send_time is None:
            self.timeout = DEFAULT_TIMEOUT
        else:
            self.timeout = (self.expiry - previous_packet_send_time).total_seconds()

    def generate_packet(self, data):
        # Assign the file data.
        self.data = data if len(data) != 0 else b""
        self.packet = self.header + self.data
        return self.packet

    def __str__(self):
        # For debugging purpose only
        return f"Sq_number: {self.sq_number}, sent at: {self.send_time}, length of Buffer: {len(self.data)}"


class IncorrectSequenceNumber(Exception):
    pass


def gbn_server(iface: str, port: int, fp: BinaryIO) -> None:
    last_seen_header = None
    sequence_number = 0
    seen_headers = set()

    with socket(AF_INET, SOCK_DGRAM) as a_socket:
        a_socket.bind((iface, port))

        print("Hello, I am a Server")
        while True:
            expected_packet = pack("!h", sequence_number)

            packet, (host, port) = a_socket.recvfrom(258)
            header = packet[:2]

            # check for what header we are receiving.
            if last_seen_header is None or expected_packet == header:
                last_seen_header = header
                seen_headers.add(header)

                a_socket.sendto(last_seen_header, (host, port))

                data = packet[2:]
                if len(data) == 0:
                    break
                else:
                    fp.write(data)

                sequence_number += 1

            elif header in seen_headers:
                a_socket.sendto(header, (host, port))
            else:
                a_socket.sendto(last_seen_header, (host, port))

        a_socket.sendto(last_seen_header, (host, port))


def gbn_client(host: str, port: int, fp: BinaryIO) -> None:
    window_size = 8
    sequence_number = 0
    exit_client, exit_idx = False, None
    previous_packet_send_time = None

    with socket(AF_INET, SOCK_DGRAM) as a_socket:
        print("Hello, I am a client")

        a_socket.settimeout(DEFAULT_TIMEOUT)

        while True:
            timeouts = 0

            rudp_packet_queue = deque(
                [
                    RUDPPacket(sequence_number=_)
                    for _ in range(sequence_number, sequence_number + window_size)
                ]
            )

            # Required for buffering ACKS for out of order packets.
            current_window_idx = {}

            # Generating window with data ...
            for window_index in range(window_size):

                data = fp.read(MESSAGE_SIZE)
                if not exit_client:
                    exit_client = len(data) == 0
                    exit_idx = window_index

                rudp_object = rudp_packet_queue[window_index]

                # Generate actual packet and send the packet.
                packet = rudp_object.generate_packet(data)
                a_socket.sendto(packet, (host, port))

                # Generate timeouts and store to send times
                rudp_object.generate_timeouts(previous_packet_send_time)
                previous_packet_send_time = rudp_object.expiry

                # Required for buffering ACKS for out of order packets.
                current_window_idx[rudp_object.header] = False

            # Modify window size in case of the last packet.
            current_window_size = exit_idx + 1 if exit_client else window_size

            # wait for acknowledgement of packets in current window
            window_index = 0
            while window_index < current_window_size:

                rudp_object = rudp_packet_queue[window_index]
                if not current_window_idx[rudp_object.header]:
                    a_socket.settimeout(rudp_object.timeout)

                    try:
                        sq_number, (host, port) = a_socket.recvfrom(2)

                        # Buffer out of order acks.
                        if not current_window_idx.get(sq_number, True):
                            current_window_idx[sq_number] = True

                        if rudp_object.header != sq_number:
                            raise IncorrectSequenceNumber()

                        window_index += 1

                    except (timeout, IncorrectSequenceNumber):
                        timeouts += 1
                        previous_packet_send_time = None

                        # send packets for remaining window again...
                        for idx in range(window_index, current_window_size):
                            rudp_object = rudp_packet_queue[idx]

                            # send packets which are yet to be acknowledged.
                            if not current_window_idx[rudp_object.header]:
                                a_socket.sendto(rudp_object.packet, (host, port))

                                rudp_object.generate_timeouts(previous_packet_send_time)
                else:
                    window_index += 1

            # after acknowledgement of empty data.
            if exit_client:
                break

            # increment sequence numbers
            sequence_number += window_size

            # AIMD
            window_size = (
                window_size + 1 if timeouts <= window_size else max(1, window_size // 2)
            )

    fp.close()
