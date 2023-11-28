import socket
from pymitter import EventEmitter
from threading import *
from logging import getLogger
event_emitter = EventEmitter()


class ServerThread(Thread):
    def __init__(self, ip: str, port: int) -> None:
        Thread.__init__(self)
        self.logger = getLogger("acb.core")
        self.address = ip
        self.port = port
        self.client = socket.socket()

    def run(self):
        self.client.bind((self.address, self.port))

        self.logger.info(f'Server is listening on {self.address}:{self.port}'.format(
            self.address, self.port))

        while True:
            self.client.listen(5)
            client, address = self.client.accept()

            self.logger.info('New connection from {}'.format(address[0]))
            ClientThread(client).start()


class ClientThread(Thread):
    def __init__(self, client: socket.socket) -> None:
        Thread.__init__(self)
        self.logger = getLogger("acb.core")
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
                self.logger.debug(
                    f"Instance: {instance_number}, CommandId: {command_id}, Length: {length}, Version: {version}, Data: {data}")
                event_emitter.emit(
                    f"{instance_number}:{command_id}", data.decode('utf-8'))
