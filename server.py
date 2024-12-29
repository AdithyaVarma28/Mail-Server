import socket
from threading import Thread
import sqlite3

class Server:
    def __init__(self,HOST,PORT):
        self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.bind((HOST,PORT))
        self.socket.listen()
        self.setup_database()
        print("Server waiting for connections...")
        self.accept_clients()

    def setup_database(self):
        conn=sqlite3.connect("server_messages.db")
        cursor=conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_email TEXT,
                receiver_email TEXT,
                message TEXT
            )
        """)
        conn.commit()
        conn.close()

    def save_message_to_db(self,sender_email,receiver_email,message):
        conn=sqlite3.connect("server_messages.db")
        cursor=conn.cursor()
        cursor.execute("INSERT INTO messages (sender_email,receiver_email,message) VALUES (?,?,?)",
                       (sender_email,receiver_email,message))
        conn.commit()
        conn.close()

    def fetch_messages_for_email(self,email):
        conn=sqlite3.connect("server_messages.db")
        cursor=conn.cursor()
        cursor.execute("SELECT sender_email,receiver_email,message FROM messages WHERE receiver_email=?",(email,))
        messages=cursor.fetchall()
        conn.close()
        return messages

    def delete_messages_for_email(self,email):
        conn=sqlite3.connect("server_messages.db")
        cursor=conn.cursor()
        cursor.execute("DELETE FROM messages WHERE receiver_email=?",(email,))
        conn.commit()
        conn.close()

    def accept_clients(self):
        while True:
            client_socket,address=self.socket.accept()
            print(f"Connection from: {str(address)}")
            Thread(target=self.talk_to_client,args=(client_socket,)).start()

    def talk_to_client(self,client_socket):
        while True:
            try:
                client_message=client_socket.recv(1024).decode()
                if client_message.startswith("SEND_EMAIL"):
                    _,sender,receiver,message=client_message.split("|",3)
                    self.save_message_to_db(sender,receiver,message)
                    client_socket.send("Email sent successfully.".encode())
                elif client_message.startswith("REQUEST_EMAILS"):
                    _,email=client_message.split("|",1)
                    messages=self.fetch_messages_for_email(email)
                    if messages:
                        response="\n".join(
                            [f"EMAIL_DATA|{sender}|{receiver}|{message}" for sender,receiver,message in messages]
                        )
                        client_socket.send(response.encode())
                    else:
                        client_socket.send("No emails found for your address.".encode())
                elif client_message.startswith("DELETE_EMAILS"):
                    _,email=client_message.split("|",1)
                    self.delete_messages_for_email(email)
                    client_socket.send("Emails deleted successfully.".encode())
                elif client_message.strip()=="DISCONNECT":
                    print("Client disconnected. Closing connection...")
                    client_socket.close()
                    break
                else:
                    print(f"Client: {client_message}")
            except ConnectionResetError:
                print("Client disconnected abruptly. Closing connection...")
                client_socket.close()
                break

Server("0.0.0.0",6969)