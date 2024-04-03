import socket
import select


#possibly refactor to include message headers like with message lengths

SERVER_IP, SERVER_PORT = "localhost", 12345
#create server socket, allow for reusability, bind and start listening
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen()


#for select
sockets_list = [server_socket]
#contains clients
clients = {}



def receive_message(client_socket):      
    #try getting message, if doesn't exist return None, otherwise return data
    try: 
        message = client_socket.recv(1024)
        if not len(message) or len(message) == 0:
            return None
        return {'data': message}
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

            #if there's no message or connection ended
            if user is None:
                continue 

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
            
            print("Message from ", clients[notified_socket])

            #send message to every client 
            for client_socket in clients:
                client_socket.send(clients[notified_socket] + ": ".encode() + message['data'])

        #handle any sockets that have any errors
        for notified_socket in exception_sockets:
            # Remove from list for socket.socket()
            sockets_list.remove(notified_socket)
            # Remove from our list of users
            del clients[notified_socket]







        

    