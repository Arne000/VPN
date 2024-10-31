import socket

PORT=9998

class PracticeClient:
    def get_host():
        try:
            Host=socket.getHost()
        except Exception as e:
            print(f"Error: {e}")

#Creating a clientsocket, internet ipv4 w/ tcp
clientSocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#Attempts a connection to the host socket, feeding host address and port
clientSocket.connect((socket.gethostname(), PORT))
#Client socket is snending a message, encoded w/ utf-8
clientSocket.send(f"Hello, this is my message".encode('utf-8'))
print(clientSocket.recv(1024).decode("utf-8"))