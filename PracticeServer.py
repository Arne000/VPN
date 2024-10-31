import socket




PORT=9998

#ipv4 internet socket, TCP connection



class PracticeServer:

    #Fetches the local host
    def get_host():
        try:
            Host=socket.gethostname()
        except Exception as e:
            print(f"error {e}")

            
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((socket.gethostname(), PORT))
server.listen(5)


while True:
    #This new socket becomes the endpoint for the server
    communication_socket, address = server.accept()
    print(f"Connected to {address}")
    #Takes a message from the client. Messages sent via sockets are encoded as bytestreams, must decode
    message = communication_socket.recv(1024).decode('utf-8')
    print(f"Message from client is: {message}")
    #sends a message from the server to the client, encoded
    communication_socket.send(f"Message received :)".encode('utf-8'))
    #closses communication, de-establising connection
    communication_socket.close()
    print(f"Connection with {address} terminated")