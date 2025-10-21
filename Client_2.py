import socket
import json
import threading
import sys

Server_PORT = 9998
Server_adr = "192.168.10.156"  # Server IP
server_connection = False

communication_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

while not server_connection:
    try:
        print(f"Attempting connection to the server: {Server_adr}:{Server_PORT} ...")
        communication_socket.connect((Server_adr, Server_PORT))
        print(f"Successfully connected to the server: {Server_adr}:{Server_PORT}!")
        server_connection = True
    except Exception as e:
        print(f"Connection to server unsuccessful. Error: {e}")
        input("Press any key to try again")

client_id = input("Enter your client ID: ")
communication_socket.sendall(client_id.encode('utf-8'))

response = communication_socket.recv(1024).decode('utf-8')
if response.startswith("ERROR"):
    print(f"Server error: {response}")
    communication_socket.close()
    sys.exit()
elif response == "OK":
    pass  
else:
    print(f"Unexpected response from server: {response}")
    communication_socket.close()
    sys.exit()

ack_event = threading.Event()


def listen_for_messages():
    while True:
        try:
            data = communication_socket.recv(4096).decode("utf-8")
            if data:
                try:
                    message = json.loads(data)
                    command = message.get("command")
                    if command == "list_clients_response":
                        clients = message.get("clients")
                        print("\nConnected clients:")
                        for c in clients:
                            print(f"- {c}")
                    elif command == "ack":
                        # Acknowledgment received
                        ack_event.set()
                    elif command == "nack":
                        # Negative acknowledgment received
                        print("Failed to send the message.")
                    else:
                        sender = message.get("from")
                        msg = message.get("message")
                        print(f"\nMessage from {sender}: {msg}")
                except json.JSONDecodeError:
                    print(f"\nReceived invalid message: {data}")
        except Exception as e:
            print(f"Error receiving message: {e}")
            break


listen_thread = threading.Thread(target=listen_for_messages, daemon=True)
listen_thread.start()


while True:
    print("\nOptions:", flush=True)
    print("1. List connected clients", flush=True)
    print("2. Send a message", flush=True)
    print("3. Quit", flush=True)
    choice = input("Select an option: ")

    if choice == '1':

        request = json.dumps({"command": "list_clients"})
        communication_socket.sendall(request.encode('utf-8'))

    elif choice == '2':

        target_id = input("Enter the target client's ID: ")
        my_message = input("Enter your message: ")
        message = json.dumps({
            "command": "send_message",
            "target_id": target_id,
            "message": my_message
        })
        communication_socket.sendall(message.encode("utf-8"))
        print("Waiting for acknowledgment...")
        ack_received = ack_event.wait(timeout=5)
        if ack_received:
            print("Message successfully sent!")
            ack_event.clear()  
        else:
            print("Failed to receive acknowledgment.")

    elif choice == '3':
        communication_socket.close()
        sys.exit()

    else:
        print("Invalid option. Please try again.")
