import socket
import threading
import unicurses
import sys

#generate fernet key for client
from cryptography.fernet import Fernet
key = Fernet.generate_key()


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
    'message': 'message',
    'whisper': 'whisper'
}




# Create a TCP/IP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
server_address = ('localhost', 12345)
client_socket.connect(server_address)



#init unicurses
stdscr = unicurses.initscr()
max_y, max_x = unicurses.getmaxyx(stdscr)
# Create windows for message display and command line input
message_height, message_width = max_y - 2, max_x
message_window = unicurses.newwin(message_height, message_width, 0, 0)
unicurses.scrollok(message_window, True)  # Enable scrolling for message window
unicurses.wrefresh(message_window)


command_window = unicurses.newwin(1, max_x, max_y - 1, 0)
unicurses.wrefresh(command_window)


#gets input from command window
def get_input():
    unicurses.echo()  # Enable echoing of input
    # Get input from the user
    input = unicurses.wgetstr(command_window)
    unicurses.noecho()  # Disable echoing of input
    unicurses.wrefresh(command_window)
    return input

#shows prompt for input in command window
def show_prompt(prompt): 
    # command_window.addstr(prompt)
    unicurses.waddstr(command_window, prompt)

    unicurses.wrefresh(command_window)

#displays a message on new line in message window
def show_on_message(str):
    # message_window.addstr(str + "\n")
    unicurses.waddstr(message_window, str + "\n")
    unicurses.wrefresh(message_window)





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

    #if whisper
    if(command_and_fields[0] == 'whisper' and len(command_and_fields) >= 3):
        return ('whisper', command_and_fields[1], ' '.join(command_and_fields[2:]))
    

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
    show_prompt("Enter your username: ")
    username = get_input()
    #clear command window
    unicurses.werase(command_window)
    show_on_message("Welcome " + username + "!")


    # username = input('Enter your username: ')
    header = {'message_length': len(username), 'action': ''}

    client_socket.sendall(format_message_to_server(header, username))


    #send fernet key to server
    header['message_length'] = len(key)
    client_socket.send(key)

    while True:
        show_prompt("Input a command or send message: ")
        user_input = get_input()

        commandAndFields = parse_command(user_input)

        match commandAndFields[0]:
            #default message (they don't need to actually enter a command to do this)
            case 'message':
               
                f = Fernet(key)
                encrypted_message = f.encrypt(commandAndFields[1].encode()).decode()
                header['message_length'] = len(encrypted_message)
            
                header['action'] = server_command_dict['message']
                client_socket.sendall(format_message_to_server(header, encrypted_message))
                unicurses.werase(command_window)
            #change username
            case 'change-username':
                if (len(commandAndFields) >= 2):
                    f = Fernet(key)
                    encrypted_username = f.encrypt(commandAndFields[1].encode()).decode()

                    header['message_length'] = len(encrypted_username)
                    header['action'] = server_command_dict['change-username']
                    client_socket.sendall(format_message_to_server(header, encrypted_username))
                    show_on_message("You are now " + commandAndFields[1])
                else: 
                    show_on_message("You need to provide a new username after the command")
                unicurses.werase(command_window)

            #whisper 
            case 'whisper':

                if(len(commandAndFields) >=3):
                    f = Fernet(key)
                    body = commandAndFields[1] + " " + commandAndFields[2]
                    print(body)
                    encrypted_body = f.encrypt(body.encode()).decode()
                    header['message_length'] = len(encrypted_body)
                    header['action'] = server_command_dict['whisper']
                    client_socket.sendall(format_message_to_server(header, encrypted_body))

                else:
                    show_on_message("You need to provide a username followed by a description")
                unicurses.wclear(command_window)
                
            #lists commands
            case 'help':
                commands_help = "/change-username - enter username after this command to change username\n/q - quits application\n/whisper -accepts username followed by message to send to user "
                show_on_message(commands_help)
                unicurses.werase(command_window)
            #not sure why quitting isn't working
            case 'q':
                message_window.addstr("Goodbye!")
                unicurses.wrefresh(message_window)
                sys.exit(0)
            #invalid command
            case _:
                show_on_message("Invalid command")
                unicurses.werase(command_window)





# Function receive messages from server
def receive_message():
    while True:
        #decode using our key
        f = Fernet(key)
        message = client_socket.recv(1024)
        message = f.decrypt(message).decode()
        if message:
            show_on_message(message)





def main(stdscr):
    unicurses.curs_set(1)  # Set cursor to be visible
    unicurses.refresh()

    

    # Start threads for sending and receiving messages
    send_thread = threading.Thread(target=send_message)
    receive_thread = threading.Thread(target=receive_message)

    send_thread.start()
    receive_thread.start()

    send_thread.join()
    receive_thread.join()

    client_socket.close()
unicurses.wrapper(main)