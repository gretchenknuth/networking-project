from socket import *
import threading

# servername = server IP
serverName = ""
serverPort = 45231

# create TCP socket and connect to server
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

# Display the client’s local address and port information
print(f"Client is running on {clientSocket.getsockname()}")

'''
Start a background thread to continuously:
    - Receive incoming messages from the server
    - Display received messages to the user
'''
def receive_messages():
    while True:
        try:
            message = clientSocket.recv(1024).decode()
            if message:
                print(f"\nReceived: {message}")
            else:
                print("\nServer closed the connection.")
                break
        except:
            print("\nError receiving message.")
            break
        
'''
In the main thread, repeatedly:
    - Accept user input from the keyboard
    - Send the typed message to the server
'''
def send_messages():
    while True:
        message = input("Enter message to send (or 'q' to quit): ")
        if message.lower() == 'q':
            break
        try:
            clientSocket.sendall(message.encode())
        except:
            print("Error sending message.")
            break
        