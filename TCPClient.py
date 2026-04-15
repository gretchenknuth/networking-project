from socket import *

# servername = server IP
serverName = ""
serverPort = 45231

# create TCP socket and connect to server
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))