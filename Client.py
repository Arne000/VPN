import socket
import json
import threading
import sys

Server_PORT = 9998
Server_adr = "192.168.10.156"  # Server IP
server_connection = False

# Create a socket for communication with the server
communication_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
while not server_connection:
    try:
        print(f"Attempting connection to the server: {Server_adr}:{Server_PORT} ...")
        communication_socket.connect((Server_adr, Server_PORT))
        print(f"Successfully connected to the server: {Server_adr}:{Server_PORT}!")
        server_connection = True
    except Exception as e:
        print(f"Connection to server unsuccessful. Error: {e}")
        input("Press any key to try again")

# Sending client ID to the server
client_id = input("Enter your client ID: ")
communication_socket.sendall(client_id.encode('utf-8'))

# Checking for server response after sending client ID
response = communication_socket.recv(1024).decode('utf-8')
if response.startswith("ERROR"):
    print(f"Server error: {response}")
    communication_socket.close()
    sys.exit()
elif response == "OK":
    pass  # Just a syntax placeholder, probably going to add/change some stuff here later.
else:
    print(f"Unexpected response from server: {response}")
    communication_socket.close()
    sys.exit()

# Program was stuck due to race condition. Now only one thread reads from the socket.
#Important note for future development:
#Potential problem. This solution assumes the threads never need to process the same type of message
#I.E: If both threads cares about the contents of an "ack" message, we have a problem. 
ack_event = threading.Event()

# Function to listen for incoming messages from the server
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

# Start a thread to listen for incoming messages
listen_thread = threading.Thread(target=listen_for_messages, daemon=True)
listen_thread.start()

# Main loop to interact with the user
while True:
    print("\nOptions:", flush=True)
    print("1. List connected clients", flush=True)
    print("2. Send a message", flush=True)
    print("3. Quit", flush=True)
    choice = input("Select an option: ")

    if choice == '1':
        # Request the list of connected clients
        request = json.dumps({"command": "list_clients"})
        communication_socket.sendall(request.encode('utf-8'))

    elif choice == '2':
        # Send a message to a client
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
            ack_event.clear()  # Reset the event for next time
        else:
            print("Failed to receive acknowledgment.")

    elif choice == '3':
        communication_socket.close()
        sys.exit()

    else:
        print("Invalid option. Please try again.")
