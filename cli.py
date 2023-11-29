import socket

# Server details
host = 'localhost'  # Change this to the IP address or hostname of the server
port = 9339  # The port you want to connect to

# Data to be sent
data_to_send = "Moin"

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
server_address = (host, port)
client_socket.connect(server_address)

instance_number = 1
message = "./test1.png"
command_id = 2
message_bytes = bytes(message, 'utf-8')
message_length = len(message_bytes)
version = 1
data = b''.join([instance_number.to_bytes(2, 'big'), command_id.to_bytes(
    2, 'big'), message_length.to_bytes(3, 'big'), version.to_bytes(2, 'big'), message_bytes])

# Send data
client_socket.sendall(data)
# Close the connection
client_socket.close()
