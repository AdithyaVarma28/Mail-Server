import socket
from threading import Thread,Event
import os

class Client:
    def __init__(self,HOST,PORT):
        self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.connect((HOST,PORT))
        self.response_event=Event()
        self.talk_to_server()

    def talk_to_server(self):
        Thread(target=self.receive_message).start()
        self.send_message()

    def send_message(self):
        while True:
            self.response_event.clear()
            print("\nOptions:")
            print("1. Send Email")
            print("2. Request Emails for Your Address")
            print("3. Delete Emails for Your Address")
            print("4. Exit")
            choice=input("Enter your choice: ")
            if choice=="1":
                sender=input("Enter your email: ")
                receiver=input("Enter receiver's email: ")
                message=input("Enter your message: ")
                self.socket.send(f"SEND_EMAIL|{sender}|{receiver}|{message}".encode())
            elif choice=="2":
                email=input("Enter your email to retrieve messages: ")
                self.socket.send(f"REQUEST_EMAILS|{email}".encode())
            elif choice=="3":
                email=input("Enter your email to delete messages: ")
                self.socket.send(f"DELETE_EMAILS|{email}".encode())
            elif choice=="4":
                self.socket.send("DISCONNECT".encode())
                print("Exiting...")
                os._exit(0)
            else:
                print("Invalid choice. Try again.")
            self.response_event.wait()

    def receive_message(self):
        while True:
            try:
                server_message=self.socket.recv(1024).decode()
                if server_message.startswith("EMAIL_DATA"):
                    _,sender,receiver,message=server_message.split("|",3)
                    print(f"\nNew Email Received:\nFrom: {sender}\nTo: {receiver}\nMessage: {message}")
                elif server_message.strip()=="No emails found for your address.":
                    print("\nServer: No emails found for your address.")
                elif server_message.strip()=="Email sent successfully.":
                    print("\nServer: Email sent successfully.")
                elif server_message.strip()=="Emails deleted successfully.":
                    print("\nServer: Emails deleted successfully.")
                elif not server_message.strip():
                    print("Server has disconnected. Exiting...")
                    os._exit(0)
                else:
                    print(f"Server: {server_message}")
                self.response_event.set()
            except ConnectionResetError:
                print("Server disconnected abruptly. Exiting...")
                os._exit(0)

Client("127.0.0.1",6969)