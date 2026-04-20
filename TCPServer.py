from socket import *
import threading

# Replace '' with our IP address for vid!!
IP = ""
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

            message = data.decode().strip()
            
            if message.startswith("@"):
                # Direct message
                split = message.split(" ", 1)
                target = split[0][1:]
                content = split[1] if len(split) > 1 else ""

                with clients_lock:
                    if target in active_clients:
                        active_clients[target].sendall(f"[from {user}] {content}".encode())
                        conn.sendall(f"[to {target}] {content}".encode())
                    else:
                        conn.sendall(f"User '{target}' not found".encode())
            else:
                # Broadcast message to all other clients
                with clients_lock:
                    for other_user, client in active_clients.items():
                        if client != conn:
                            client.sendall(f"[from {user}] {message}".encode())
        except:
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
    connection_socket.sendall("Enter username: ".encode())
    username = connection_socket.recv(1024).decode().strip()

    with clients_lock:
        # Ensure unique usernames without spaces
        while username in active_clients or " " in username:
            if username in active_clients:
                connection_socket.sendall("Username taken. Try another: ".encode())
            else:
                connection_socket.sendall("Username cannot contain spaces. Try another: ".encode())
            username = connection_socket.recv(1024).decode().strip()
        # Add username and socket to client dict
        active_clients[username] = connection_socket

    # Start a new thread to handle communication with client
    thread = threading.Thread(target=handle_client, args=(connection_socket, client_addr, username))
    thread.start()
