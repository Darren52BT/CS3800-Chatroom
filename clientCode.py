import socket
import threading

class Client:
    #we will send message to server with header
    #header is formatted like cookie
    #header components:

    #   message_length: contains int for message length
    #   action: contains string denoting what action is taking place
    HEADER_LENGTH = 50


    # Current possible values for action:
        # "message" = sending message
        # "change-username" - changing username


    #dict for mapping commands to server action verbs

    server_command_dict = {
        'change-username': 'change-username',
        'message': 'message'
    }

    def __init__(self):
        # Create a TCP/IP socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to the server
        self.server_address = ('localhost', 12345)
        self.client_socket.connect(self.server_address)

        # Start threads for sending and receiving messages
        send_thread = threading.Thread(target=self.send_message())
        receive_thread = threading.Thread(target=self.receive_message())

        send_thread.start()
        receive_thread.start()

        send_thread.join()
        receive_thread.join()

        self.client_socket.close()



    #HELPER FUNCTIONS

    #format dict object into header string
    @staticmethod
    def format_header(header_obj):
        header_string = ';'.join(['='.join([str(key), str(value)]) for key, value in header_obj.items()])
        return header_string

    #parse user input for commands and other fields, assuming that command start with /,
    #command is first in list, fields are after
    @staticmethod
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
    def format_message_to_server(self, header_obj, message_body):
        #the header is a fixed length so we need to pad the middle with white spaces if the header is lower
        formatted_header = self.format_header(header_obj)
        missing_header_length = self.HEADER_LENGTH - len(formatted_header) 
        missing_header_length = missing_header_length if missing_header_length > 0 else 0


        return (formatted_header+ " " * missing_header_length  + message_body).encode()

    # Function to send messages to the server
    def send_message(self):

        username = input('Enter your username: ')
        header = {'message_length': len(username), 'action': ''}

        self.client_socket.sendall(self.format_message_to_server(header, username))


        while True:
            user_input = input('Input a command or send message:')

            commandAndFields = self.parse_command(user_input)

            match commandAndFields[0]:
                case 'message':
                    header['message_length'] = len(commandAndFields[1])
                    header['action'] = self.server_command_dict['message']
                    self.client_socket.sendall(self.format_message_to_server(header, commandAndFields[1]))
                case 'change-username':
                    header['message_length'] = len(commandAndFields[1])
                    header['action'] = self.server_command_dict['change-username']
                    self.client_socket.sendall(self.format_message_to_server(header, commandAndFields[1]))
                case _:
                    print("invalid command")

    # Function receive messages from server
    def receive_message(self):
        while True:
            message = self.client_socket.recv(1024).decode()
            if message:
                print(message)

test = Client()