import socket
import threading
HEADER_LENGTH = 50


#we will send message to server with header
#header is formatted like cookie
#header components:

#   message_length: contains int for message length
#   action: contains string denoting what action is taking place


# Current possible values for action:
    # "message" = sending message
    # "change-username" - changing username
    

#dict for mapping commands to server action verbs

server_command_dict = {
    'change-username': 'change-username',
    'message': 'message'
}


# Create a TCP/IP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
server_address = ('localhost', 12345)
client_socket.connect(server_address)



#HELPER FUNCTIONS

#format dict object into header string
def format_header(header_obj):
    header_string = ';'.join(['='.join([str(key), str(value)]) for key, value in header_obj.items()])
    return header_string

#parse user input for commands and other fields, assuming that command start with /,
#command is first in list, fields are after

def parse_command(input):

    command_and_fields = input.strip()

    #if no length return None
    if(len(command_and_fields) == 0):
        return (None)
    
    #if no slash at beginning treat as though it is message,
    if(command_and_fields[0] != '/'):
        return ('message', command_and_fields)
    
    command_and_fields = list(filter(lambda x: len(x) > 0, command_and_fields[1:].split(' ')))

    return command_and_fields 

#append formatted header and message body into one string 
def format_message_to_server(header_obj, message_body):
    #the header is a fixed length so we need to pad the middle with white spaces if the header is lower
    formatted_header = format_header(header_obj)
    missing_header_length = HEADER_LENGTH - len(formatted_header) 
    missing_header_length = missing_header_length if missing_header_length > 0 else 0


    return (formatted_header+ " " * missing_header_length  + message_body).encode()


    



# Function to send messages to the server
def send_message():

    username = input('Enter your username: ')
    header = {'message_length': len(username), 'action': ''}

    client_socket.sendall(format_message_to_server(header, username))


    while True:
        user_input = input('Input a command or send message:')
        
        commandAndFields = parse_command(user_input)

        match commandAndFields[0]:
            case 'message':
                header['message_length'] = len(commandAndFields[1])
                header['action'] = server_command_dict['message']
                client_socket.sendall(format_message_to_server(header, commandAndFields[1]))
            case 'change-username':
                header['message_length'] = len(commandAndFields[1])
                header['action'] = server_command_dict['change-username']
                client_socket.sendall(format_message_to_server(header, commandAndFields[1]))
            case _:
                print("invalid command")



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
