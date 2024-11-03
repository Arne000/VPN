import socket
import threading
import json

# Server configuration
PORT = 9998
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind server to its IP and PORT. Remember to change when deploying the server as a proxy :)
server_socket.bind((socket.gethostname(), PORT))
server_socket.listen(5)

print(f"Server is listening on port {PORT}...")

# Dictionary to store connected clients
connected_clients = {}  # Key: client_id, Value: client_socket

# Lock for thread-safe operations on my connected clients
client_lock = threading.Lock()

# Client handling
def handle_client(client_socket, client_address):
    print(f"New connection from {client_address}")

    # Takes the ID from the client
    try:
        client_id = client_socket.recv(1024).decode('utf-8').strip()
        print(f"Client connected with ID: {client_id}")
    except Exception as e:
        print(f"Failed to receive client ID from {client_address}: {e}")
        client_socket.close()
        return

    # Register the client
    with client_lock:
        if client_id in connected_clients:
            # Client ID already exists
            client_socket.sendall("ERROR: Client ID already in use.".encode('utf-8'))
            client_socket.close()
            print(f"Connection closed for {client_id} due to duplicate ID")
            return
        connected_clients[client_id] = client_socket

    # Send acknowledgment to the client
    client_socket.sendall("OK".encode('utf-8'))

    connected = True
    while connected:
        try:
            # Receive data from the client
            data = client_socket.recv(4096).decode("utf-8")
            if not data:
                print(f"Connection closed by {client_id}")
                break

            print(f"Received data from {client_id}: {data}")
            message = json.loads(data)

            command = message.get("command")

            # List the clients
            if command == "list_clients":
                with client_lock:
                    client_list = list(connected_clients.keys())
                response = json.dumps({"command": "list_clients_response", "clients": client_list})
                client_socket.sendall(response.encode('utf-8'))

            # Send a message
            elif command == "send_message":
                msg = message.get("message")
                target_id = message.get("target_id")
                print(f"Message from {client_id} to {target_id}: {msg}")

                # Look up the target client
                with client_lock:
                    target_client = connected_clients.get(target_id)

                if target_client:
                    try:
                        forward_message = json.dumps({
                            "from": client_id,
                            "message": msg
                        })
                        #Send the message to the targeted client after formatting
                        target_client.sendall(forward_message.encode("utf-8"))
                        ack_message = json.dumps({"command": "ack"})
                        client_socket.sendall(ack_message.encode("utf-8"))
                    except Exception as e:
                        # Some sort of error
                        print(f"Error sending message to {target_id}: {e}")
                        nack_message = json.dumps({"command": "nack"})
                        client_socket.sendall(nack_message.encode("utf-8"))
                else:
                    # ID for taget client not found
                    print(f"Target client {target_id} not found.")
                    nack_message = json.dumps({"command": "nack"})
                    client_socket.sendall(nack_message.encode("utf-8"))

            else:
                # Handle unknown command
                print(f"Unknown command '{command}' from {client_id}")
                nack_message = json.dumps({"command": "nack"})
                client_socket.sendall(nack_message.encode("utf-8"))

        except json.JSONDecodeError:
            # In case the payload isn't valid JSON
            print(f"Error: Received invalid JSON from {client_id}")
            nack_message = json.dumps({"command": "nack"})
            client_socket.sendall(nack_message.encode("utf-8"))
        except Exception as e:
            # Just a catch-all exception if all else fails
            print(f"Error handling client {client_id}: {e}")
            connected = False

    # Remove the client from our storage
    with client_lock:
        if client_id in connected_clients:
            del connected_clients[client_id]

    # Close the client socket
    client_socket.close()
    print(f"Connection closed for {client_id}")

# Main server loop to accept incoming client connections
while True:
    client_socket, client_address = server_socket.accept()
    client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    client_thread.start()
