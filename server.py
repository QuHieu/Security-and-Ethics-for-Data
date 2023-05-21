import socket
import threading
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
import os
from datetime import datetime

class ChatServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = {}
        self.key = b'mysecretpassword'  # Encryption key
        self.history = []

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()

        print("Chat server started.")

        while True:
            client_socket, address = self.server_socket.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

    def handle_client(self, client_socket):
        username = client_socket.recv(1024).decode()
        print(f"{username} connected.")
        # Send previous chat history to the new user
        if self.history != []:
            for message in self.history:
                client_socket.send(message.encode())

        self.clients[username] = client_socket
        self.broadcast(f"{username} joined the chat.", sender=client_socket)
        # self.broadcast(f"{username} joined the chat.")
        
        log_filename = datetime.now().strftime("%Y-%m-%d.txt")
        if not os.path.exists(log_filename):
            with open(log_filename, "w") as log_file:
                log_file.write("Chat Log:\n")

        self.clients[username] = client_socket

        while True:
            try:
                encrypted_message = client_socket.recv(1024)
                if encrypted_message:
                    message = self.decrypt_message(encrypted_message)
                    self.broadcast(f"{username}: {message}", sender=client_socket)
                    if message == "exit":
                        break
                    print(f"{username}: {encrypted_message}")
                    self.history.append(f"[HISTORY]{username}: {encrypted_message}")
                    with open(log_filename, "a") as log_file:
                        log_file.write(f"{username}: {encrypted_message}" + "\n")
            except:
                break

        del self.clients[username]
        self.broadcast(f"{username} left the chat.", sender=client_socket)
        client_socket.close()

    def broadcast(self, message, sender):
        # for client_socket in self.clients.values():
        #     client_socket.send(self.encrypt_message(message))
        for client_username, client_socket in self.clients.items():
            if client_socket != sender:
                client_socket.send(self.encrypt_message(message))

    def encrypt_message(self, message):
        cipher = AES.new(self.key, AES.MODE_CBC)
        cipher_text = cipher.encrypt(pad(message.encode(), AES.block_size))
        return cipher.iv + cipher_text

    def decrypt_message(self, encrypted_message):
        iv = encrypted_message[:AES.block_size]
        cipher_text = encrypted_message[AES.block_size:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted_message = unpad(cipher.decrypt(cipher_text), AES.block_size)
        return decrypted_message.decode()

    def shutdown(self):
        self.server_socket.close()


def main():
    host = 'localhost'
    port = 8000

    chat_server = ChatServer(host, port)
    try:
        chat_server.start()
    except KeyboardInterrupt:
        print("Chat server shutting down...")
        chat_server.shutdown()


if __name__ == "__main__":
    main()