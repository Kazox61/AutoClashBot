import socket
from pymitter import EventEmitter
from threading import *

event_emitter = EventEmitter()


class ServerThread(Thread):
    def __init__(self, ip: str, port: int) -> None:
        Thread.__init__(self)
        self.address = ip
        self.port = port
        self.client = socket.socket()

    def run(self):
        self.client.bind((self.address, self.port))

        print(f'Server is listening on {self.address}:{self.port}'.format(
            self.address, self.port))

        while True:
            self.client.listen(5)
            client, address = self.client.accept()

            print('New connection from {}'.format(address[0]))
            clientThread = ClientThread(client).start()


class ClientThread(Thread):
    def __init__(self, client: socket.socket) -> None:
        Thread.__init__(self)
        self.client = client

    def recvall(self, size) -> bytes:
        data = []
        while size > 0:
            self.client.settimeout(5.0)
            s = self.client.recv(size)
            self.client.settimeout(None)
            if not s:
                raise EOFError
            data.append(s)
            size -= len(s)
        return b''.join(data)

    def run(self) -> None:
        while True:
            header = self.client.recv(9)
            instance_number = int.from_bytes(header[:2], 'big')
            command_id = int.from_bytes(header[2:4], 'big')
            length = int.from_bytes(header[4:7], 'big')
            version = int.from_bytes(header[7:], 'big')
            data = self.recvall(length)

            if len(header) >= 9:
                print(
                    f"Instance: {instance_number}, CommandId: {command_id}, Length: {length}, Version: {version}, Data: {data}")
                event_emitter.emit(f"{instance_number}:{command_id}", data)
