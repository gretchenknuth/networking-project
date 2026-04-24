from socket import *
import threading

# feature 3: AES encryption for messages
from cryptography.fernet import Fernet

SECRET_KEY = b'HcCQN4C65TCgQN5FXy9lTkW1AP1A4bZ01tBjvqNJJRs=' 
cipher_suite = Fernet(SECRET_KEY)

def encrypt_msg(message):
    return cipher_suite.encrypt(message.encode())

def decrypt_msg(token):
    return cipher_suite.decrypt(token).decode()

# servername = server IP
serverName = "172.20.10.2"
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
try:
    prompt = decrypt_msg(clientSocket.recv(1024))
    username = input(prompt)
    clientSocket.sendall(encrypt_msg(username))
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
            # Receive the encrypted token
            token = clientSocket.recv(2048) 
            if token:
                # DECRYPT here before printing
                message = decrypt_msg(token)
                print(f"\nReceived (Decrypted): {message}")
            else:
                break
        except Exception as e:
            print(f"\nDecryption/Receive Error: {e}")
            break
           
'''
In the main thread, repeatedly:
    - Accept user input from the keyboard
    - Send the typed message to the server
'''
def send_messages():
    while True:
        message = input("Enter message (press q to exit): ")
        # clients can disconnect by entering the message `q`
        if message.lower() == 'q': break
        try:
            # ENCRYPT here before sending over the wire
            encrypted_data = encrypt_msg(message)
            clientSocket.sendall(encrypted_data)
        except:
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
        