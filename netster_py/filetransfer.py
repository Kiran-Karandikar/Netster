# Standard Library
from socket import (
    AF_INET,
    SO_RCVBUF,
    SO_REUSEADDR,
    SOCK_DGRAM,
    SOCK_STREAM,
    SOL_SOCKET,
    socket,
)
from typing import BinaryIO


def file_server(iface: str, port: int, use_udp: bool, fp: BinaryIO) -> None:
    print("Hello, I am a server")
    if use_udp:
        with socket(AF_INET, SOCK_DGRAM) as a_socket:
            a_socket.bind((iface, port))
            while True:
                details = a_socket.recvfrom(256)
                data, address = details[0], details[1]
                if len(data) == 0:
                    break
                else:
                    fp.write(data)
    else:
        # Some of the below code is directly adapted from python documentation on socket programming.
        with socket(AF_INET, SOCK_STREAM) as a_socket:
            a_socket.bind((iface, port))
            a_socket.listen()
            a_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            a_socket.setsockopt(SOL_SOCKET, SO_RCVBUF, 256)
            # a_socket.settimeout(3)
            connection_object, address = a_socket.accept()
            with connection_object:
                while True:
                    data = connection_object.recv(256)
                    if len(data) == 0:
                        break
                    else:
                        fp.write(data)
    fp.close()


def file_client(host: str, port: int, use_udp: bool, fp: BinaryIO) -> None:
    message_size = 256
    print("Hello, I am a client")
    if use_udp:
        with socket(AF_INET, SOCK_DGRAM) as a_socket:
            while True:
                message = fp.read(message_size)
                if len(message) != 0:
                    a_socket.sendto(message, (host, port))
                else:
                    a_socket.sendto(b"", (host, port))
                    break
    else:
        with socket(AF_INET, SOCK_STREAM) as a_socket:
            a_socket.connect((host, port))
            # a_socket.settimeout(10)
            while True:
                message = fp.read(message_size)
                if len(message) != 0:
                    a_socket.send(message)
                else:
                    a_socket.send(b"")
                    break
    fp.close()
