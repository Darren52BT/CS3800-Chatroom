import socket
import threading

# Create a TCP/IP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
server_address = ('localhost', 12345)
client_socket.connect(server_address)

# Function to send messages to the server
def send_message():
    username = input('Enter your username: ')
    client_socket.sendall(username.encode())
    while True:
        message = input()
        client_socket.sendall(message.encode())

# Function receive messages from server
def receive_message():
    while True:
        message = client_socket.recv(1024).decode()
        if message:
            print(message)

# Start threads for sending and receiving messages
send_thread = threading.Thread(target=send_message)
receive_thread = threading.Thread(target=receive_message)

send_thread.start()
receive_thread.start()

send_thread.join()
receive_thread.join()

client_socket.close()
