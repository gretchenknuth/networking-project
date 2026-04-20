from socket import *
import threading

# servername = server IP
serverName = ""
serverPort = 45231

# create TCP socket and connect to server
try:
    print(f"Connecting to server at {serverName}:{serverPort}...")
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    print("Connected to server.")
except Exception as e:
    print(f"Failed to connect to server: {e}")
    exit(1)
    
'''
3: Wait for the server to request a username
4: Input the username from the user and send it to the server
'''
while True:
    try:
        prompt = clientSocket.recv(1024).decode()
        print(prompt, end='')  # Print the prompt without adding a new line
    
        # if asked, give the server a username to identify this client
        if "username" in prompt.lower() or "another" in prompt.lower():  
            username = input()
            clientSocket.sendall(username.encode())
        else: # if the server sent something else, ignore it
            break
    except Exception as e:
        print(f"Error during username setup: {e}")
        clientSocket.close()
        exit(1)

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
    clientSocket.close()
        
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
        
# Start the receive thread
receive_thread = threading.Thread(target=receive_messages)
receive_thread.daemon = True
receive_thread.start()

# Start sending messages in the main thread
send_messages()

# Close the socket when done
clientSocket.close()
print("Client socket closed.")
        