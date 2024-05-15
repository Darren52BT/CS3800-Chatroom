import socket
import select
from base64 import urlsafe_b64decode 
from base64 import urlsafe_b64encode 
from cryptography.fernet import Fernet
HEADER_LENGTH = 50

SERVER_IP, SERVER_PORT = "localhost", 12345
#create server socket, allow for reusability, bind and start listening
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen()

print("Server is started, awaiting connections...")

#for select
sockets_list = [server_socket]
#contains clients
clients = {}

#contains client keys
client_keys = {}

#converts header which is in cookie format into dict
def parse_header(header):
    #split by ;
    parsed_header = [item.split("=") for item in header.split(";")]
    #make sure each subarray has a header and value
    parsed_header = filter(lambda x: len(x) == 2, parsed_header)
    #convert into dict
    parsed_header = {key:value for key,value in parsed_header}
    return parsed_header

    

def receive_message(client_socket):      
    try: 
        #get header and message using header length
        message_header =  client_socket.recv(HEADER_LENGTH)
        #if there's no header, then connection closed
        if not len(message_header):
            return None
        
        #parse header
        message_header = parse_header(header=message_header.decode('utf-8').strip())

        #if there's no "message_length" header return None
        if 'message_length' not in message_header:
            return None

        message = client_socket.recv(int(message_header['message_length']))
        return {'header': message_header, 'data': message}
    
    #otherwise connection is over
    except: 
        return None
    

#loop to infinitely accept client requests
while True: 
    read_sockets, write_sockets, exception_sockets = select.select(sockets_list, [], sockets_list)

    #iterate over notified sockets 
    for notified_socket in read_sockets:

        #if socket is server socket then we have a new connection, only accept if length of clients is 10 or less
        if notified_socket == server_socket and len(clients) <=10:
            client_socket, client_address = server_socket.accept()


            #receive username
            user = receive_message(client_socket)

            # Get username from the dictionary and decode from bytecode to translate to a string for visibility
            printUser = user.get('data')
            printUser = printUser.decode("utf-8")
            print(printUser + " has connected.")

            #if there's no message or connection ended
            if user is None:
                continue 

            #receive client fernet key
            key = client_socket.recv(128).decode()

            client_keys[client_socket] = key.encode()

            #otherwise, append client socket to list of sockets to be monitored 
            #append it to clients dict with their username
            sockets_list.append(client_socket) 
            clients[client_socket] = user['data']

        #otherwise current socket is sending message
        else:
            message = receive_message(notified_socket)

            #handle disconnection
            if message is None:
                print("Closed connection from ", notified_socket)
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue 
            

            #----HANDLE ACTIONS BASED ON HEADER HERE-----#

            message_body = message['data']
            message_header = message['header']

            #decrypt message, 
            curr_sender_client_key = client_keys[notified_socket]
            f = Fernet(curr_sender_client_key)
            message_body = f.decrypt(message_body)



            match message_header['action']:
                case 'message':
                      # Get username from the clients dictionary and decode from bytecode to translate to a string for visibility
                    printClient = clients[notified_socket]
                    printClient = printClient.decode("utf-8")
                    print("Message from " + printClient + " has been received.")



                    #send message to every client except for client that sent message
                    for client_socket in clients:
                        #get key of current receiving client
                        curr_receiver_client_key = client_keys[client_socket]
                        #encrypt with their key and send to them
                        f = Fernet(curr_receiver_client_key)
                        encrypted_message = f.encrypt(clients[notified_socket] + ": ".encode() + message_body)
                        client_socket.send(encrypted_message)
                case 'change-username':
                    print(clients[notified_socket].decode('utf-8') + " is changing their name to " + message_body.decode('utf-8'))
                    clients[notified_socket] = message_body
                case _: 
                    notified_socket.send("Invalid action".encode())

       
          

        #handle any sockets that have any errors
        for notified_socket in exception_sockets:
            # Remove from list for socket.socket()
            sockets_list.remove(notified_socket)
            # Remove from our list of users
            del clients[notified_socket]







        

    