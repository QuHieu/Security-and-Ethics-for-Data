import socket
import threading
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad

class ChatClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = None
        self.key = b'mysecretpassword'  # Encryption key

    def connect(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))

        username = input("Enter your username: ")
        self.client_socket.send(username.encode())

        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

        self.send()

    def send(self):
        while True:
            message = input()
            if message == "exit":
                self.client_socket.send(self.encrypt_message("exit"))
                break
            self.client_socket.send(self.encrypt_message(message))
            
    # def history(self):
    #     while True:
    #         history = self.client_socket.recv(1024)
    #         print(history)

    def receive(self):
        while True:
            encrypted_message = self.client_socket.recv(1024)
            if encrypted_message.startswith(b"[HISTORY]"):
                chat_history = encrypted_message.decode()[9:]
                print(chat_history)
            else:
                message = self.decrypt_message(encrypted_message)
                print(message)

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


def main():
    host = 'localhost'
    port = 8000

    chat_client = ChatClient(host, port)
    try:
        chat_client.connect()
    except ConnectionRefusedError:
        print("Could not connect to the chat server.")


if __name__ == "__main__":
    main()
