from socket import *
import threading

# Replace '' with our IP address for vid!!
IP = ""
PORT = 45231
active_clients = []
clients_lock = threading.Lock()

def handle_client(conn, addr):
    print(f"{addr} connected")
    while True:
        try:
            # 1024 specifies max num bytes it will receive
            data = conn.recv(1024)
            if not data:
                break

            # Forward message to all other clients
            with clients_lock:
                for client in active_clients:
                    if client != conn:
                        client.sendall(data)
        except:
            break

    print(f"{addr} disconnected")

    # Remove from list and close connection
    with clients_lock:
        active_clients.remove(conn)

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

    # Add client to the list of active clients
    with clients_lock:
        active_clients.append(connection_socket)

    # Start a new thread to handle communication with that client
    thread = threading.Thread(target=handle_client, args=(connection_socket, client_addr))
    thread.start()
