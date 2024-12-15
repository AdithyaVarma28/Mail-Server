import socket
from threading import Thread,Event
import os
import sqlite3

class Client:
    def __init__(self,HOST,PORT):
        self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.connect((HOST,PORT))
        self.setup_local_database()
        self.response_event=Event()
        self.talk_to_server()

    def setup_local_database(self):
        self.conn=sqlite3.connect("client_messages.db")
        self.cursor=self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_email TEXT,
                receiver_email TEXT,
                message TEXT
            )
        """)
        self.conn.commit()

    def talk_to_server(self):
        Thread(target=self.receive_message).start()
        self.send_message()

    def send_message(self):
        while True:
            self.response_event.clear()
            print("\nOptions:")
            print("1. Send Email")
            print("2. Request Emails for Your Address")
            print("3. Exit")
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
                self.socket.send("DISCONNECT".encode())
                print("Exiting...")
                os._exit(0)
            else:
                print("Invalid choice. Try again.")
            self.response_event.wait()

    def receive_message(self):
        thread_conn=sqlite3.connect("client_messages.db")
        thread_cursor=thread_conn.cursor()
        while True:
            try:
                server_message=self.socket.recv(1024).decode()
                if server_message.startswith("EMAIL_DATA"):
                    _,sender,receiver,message=server_message.split("|",3)
                    thread_cursor.execute(
                        "INSERT INTO messages (sender_email,receiver_email,message) VALUES (?,?,?)",
                        (sender,receiver,message)
                    )
                    thread_conn.commit()
                    print(f"New Email Received:\nFrom: {sender}\nTo: {receiver}\nMessage: {message}")
                elif server_message.strip()=="shutdown" or not server_message.strip():
                    print("Server has disconnected. Exiting...")
                    os._exit(0)
                else:
                    print(f"Server: {server_message}")
                self.response_event.set()
            except ConnectionResetError:
                print("Server disconnected abruptly. Exiting...")
                os._exit(0)

Client("127.0.0.1",6969)