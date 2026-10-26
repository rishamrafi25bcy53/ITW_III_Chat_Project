
import socket
import threading

HOST = "0.0.0.0"
PORT = 5000

clients = {}
lock = threading.Lock()


def broadcast(message):
    data = (message + "\n").encode("utf-8")

    with lock:
        for client in list(clients.keys()):
            client.sendall(data)


def handle_client(client, address):
    reader = client.makefile("r", encoding="utf-8")
    username = reader.readline().strip()

    with lock:
        clients[client] = username

    print(username, "connected")
    broadcast(username + " joined the chat!")

    for message in reader:
        message = message.strip()

        if message == "/quit":
            break

        if message:
            broadcast(username + ": " + message)

    reader.close()
    client.close()

    with lock:
        clients.pop(client)

    print(username, "disconnected")
    broadcast(username + " left the chat!")


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.bind((HOST, PORT))
    server.listen()

    print("Server started on port", PORT)

    while True:
        client, address = server.accept()

        thread = threading.Thread(
            target=handle_client,
            args=(client, address)
        )
        thread.start()


if __name__ == "__main__":
    start_server()