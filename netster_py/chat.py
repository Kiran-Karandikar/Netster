# Standard Library
import signal

from socket import AF_INET, SOCK_DGRAM, SOCK_STREAM, socket
from threading import Event, Thread

# 3rd Party Libraries
from _socket import SO_RCVBUF, SO_REUSEADDR, SOL_SOCKET, timeout


def chat_server(iface: str, port: int, use_udp: bool) -> None:
    print("Hello, I am a server")
    close_server = False
    if use_udp:
        with socket(AF_INET, SOCK_DGRAM) as a_socket:
            a_socket.bind((iface, port))
            while not close_server:
                details = a_socket.recvfrom(256)
                data, address = details[0], details[1]
                data = data.decode()
                print("got message from ('{}', {})".format(*address))
                if data == "hello":
                    ack = "world"
                    a_socket.sendto(ack.encode(), address)
                elif data == "goodbye":
                    ack = "farewell"
                    a_socket.sendto(ack.encode(), address)
                elif data == "exit":
                    ack = "ok"
                    a_socket.sendto(ack.encode(), address)
                    close_server = True
                else:
                    ack = data
                    a_socket.sendto(ack.encode(), address)
    else:
        # Some of the below code is directly adapted from python documentation on multithreading and socket
        # programming.
        queue_length = 3
        with socket(AF_INET, SOCK_STREAM) as a_socket:
            a_socket.bind((iface, port))
            a_socket.listen(queue_length)
            a_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            a_socket.setsockopt(SOL_SOCKET, SO_RCVBUF, 256)
            a_socket.settimeout(3)
            close_server = Event()
            total_connections = 0
            all_connections = []
            while not close_server.is_set():
                try:
                    connection_object, address = a_socket.accept()
                except timeout:
                    continue
                else:
                    total_connections += 1
                    print(
                        "connection {} from ('{}', {})".format(
                            total_connections, *address
                        )
                    )
                    all_connections.append(connection_object)
                    new_thread = Thread(
                        target=process_client,
                        args=(connection_object, address, close_server),
                    )
                    new_thread.start()
        for _ in all_connections:
            try:
                with _:
                    _.send(b"ok")
            except Exception:
                continue


def process_client(connection_object, address, close_server):
    with connection_object:
        send_message = (
            lambda msg: connection_object.send(msg)
            if not close_server.is_set()
            else None
        )
        while not close_server.is_set():
            data = connection_object.recv(256).decode()
            if len(data):
                print("got message from: ('{}', {})".format(*address))
            if data == "hello":
                ack = "world"
                send_message(ack.encode())
            elif data == "goodbye":
                ack = "farewell"
                send_message(ack.encode())
                break
            elif data == "exit":
                ack = "ok"
                send_message(ack.encode())
                close_server.set()
            else:
                ack = data
                send_message(ack.encode())


def signal_handler_func(*args, **kwargs):
    raise Exception


def chat_client(host: str, port: int, use_udp: bool) -> None:
    message_size = 256
    print("Hello, I am a client")
    if use_udp:
        with socket(AF_INET, SOCK_DGRAM) as a_socket:
            while True:
                message = input("").strip()
                a_socket.sendto(message.encode(), (host, port))
                data = a_socket.recvfrom(message_size)
                print(data[0].decode())
                if message in ("goodbye", "exit"):
                    break
    else:
        with socket(AF_INET, SOCK_STREAM) as a_socket:
            a_socket.connect((host, port))
            a_socket.settimeout(10)
            while True:
                message = None
                # Some of the below code is adapted from the python documentation on signals
                # source: https://docs.python.org/3/library/signal.html#signal.SIGALRM
                # source: https://manpages.debian.org/bullseye/manpages-dev/alarm.2.en.html
                # source: https://docs.python.org/3/library/signal.html#signal.SIGALRM
                # source: https://docs.python.org/3/library/signal.html#example

                # begin  snippet
                signal.signal(signal.SIGALRM, signal_handler_func)
                signal.alarm(5)
                try:
                    message = input().strip()
                except Exception:
                    pass
                finally:
                    signal.alarm(0)
                # end snippet

                try:
                    if message:
                        a_socket.send(message.encode())
                    data = a_socket.recv(message_size).decode()
                    if data:
                        print(data)
                    if message in ("goodbye", "exit") or data == "ok":
                        break
                except BrokenPipeError:
                    break
                except Exception:
                    pass
