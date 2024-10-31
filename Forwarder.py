import socket

PORT=9998
#Connection socket, ipv4 tcp
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#bind connection socket to a port and self
server.bind((socket.gethostname(), PORT))
server.listen(5)

print(f"server is listening on port: {PORT}")
class Forwarder:
    @staticmethod
    def myFunc():
        while True:
            communication_socket, address = server.accept()
            communication_socket.send("This is a test".encode("utf-8"))
            communication_socket.close()
Forwarder.myFunc()
