from socket import *
import threading

# feature 3: AES encryption for messages
from cryptography.fernet import Fernet

# key used during encryption/decryption
SECRET_KEY = b'HcCQN4C65TCgQN5FXy9lTkW1AP1A4bZ01tBjvqNJJRs=' 
cipher_suite = Fernet(SECRET_KEY)

# function to encrypt messages
def encrypt_msg(message):
    return cipher_suite.encrypt(message.encode())

# function to decrypt messages
def decrypt_msg(token):
    return cipher_suite.decrypt(token).decode()

IP = "172.20.10.2"
PORT = 45231
active_clients = {} # username -> socket
clients_lock = threading.Lock()

def handle_client(conn, addr, user):
    print(f"{user} connected at {addr}")
    while True:
        try:
            # 1024 specifies max num bytes it will receive
            data = conn.recv(1024)
            if not data:
                break

            # server decrypts to check for "@" command
            message = decrypt_msg(data)
            
            if message.startswith("@"):
                # Direct message
                split = message.split(" ", 1)
                target = split[0][1:]
                content = split[1] if len(split) > 1 else ""

                with clients_lock:
                    if target in active_clients:
                        # if the target is a connected user, send that user a direct message
                        active_clients[target].sendall(encrypt_msg(f"[from {user}] {content}"))
                        # let the sender know that their message was sent
                        conn.sendall(encrypt_msg(f"[to {target}] {content}"))
                    else:
                        # if the target is not a conencted user, let the sender know that that user doesn't exist
                        conn.sendall(encrypt_msg(f"User '{target}' not found"))
            else:
                # Broadcast message to all other clients
                with clients_lock:
                    msg = encrypt_msg(f"[from {user}] {message}")
                    for other_user, client in active_clients.items():
                        if client != conn:
                            # send the broadcast message to every user other than the sender
                            client.sendall(msg)
                # print the encrypted message to the server console to show that it's actually doing something
                print(f"\nReceived (Encrypted): {msg}")
        except Exception as e:
            # catches any errors when dealing with the client
            print(f"Error handling client {user}: {e}") 
            break

    print(f"{user} disconnected")

    # Remove from list and close connection
    with clients_lock:
        active_clients.pop(user, None)

    conn.close()


# Create TCP socket
server_socket = socket(AF_INET, SOCK_STREAM)

# Bind socket to address and port
server_address = (IP, PORT)
server_socket.bind(server_address)

# Listen for incoming connections
server_socket.listen()
print(f"Listening on {server_address}")

while True:
    # Accept a new client connection
    connection_socket, client_addr = server_socket.accept()

    # Ask client for username
    connection_socket.sendall(encrypt_msg("Enter username: "))
    username = decrypt_msg(connection_socket.recv(1024)).strip()

    with clients_lock:
        # Ensure unique usernames without spaces
        while username in active_clients or " " in username:
            if username in active_clients:
                # if the chosen username is being used by other user, let the client choose another one
                connection_socket.sendall(encrypt_msg("Username taken. Try another: "))
            else:
                # usernames can't contain spaces due to how direct messages are parsed
                connection_socket.sendall(encrypt_msg("Username cannot contain spaces. Try another: "))
            username = decrypt_msg(connection_socket.recv(1024)).strip()
        # Add username and socket to client dict
        active_clients[username] = connection_socket

    # Start a new thread to handle communication with client
    thread = threading.Thread(target=handle_client, args=(connection_socket, client_addr, username))
    thread.start()
