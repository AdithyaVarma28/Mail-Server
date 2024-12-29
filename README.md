# Lightweight Mail Server

This project implements a lightweight email server and client system using Flask, SQLite, and Socket Programming. It ensures secure user authentication, efficient email management, and real-time communication between the server and multiple clients.

## Features

- **User Authentication**: Secure login and signup with hashed password storage.
- **Multiple Clients Support**: Handles simultaneous connections using multithreading.
- **Email Management**:
  - Send, receive, and delete emails.
  - Store emails persistently in the server-side database.
- **Socket Communication**: Real-time data exchange between clients and the server.

## Project Components

### Server Side
- Developed using Python with socket programming.
- Features:
  - Manage client connections.
  - Handle email storage, retrieval, and deletion in a SQLite database.
  - Use multithreading for concurrent client requests.

### Client Side
- Built with Flask for an intuitive web interface.
- Features:
  - User registration and authentication.
  - Send, retrieve, and delete emails via server communication.
  - Interfaces for user-friendly email management.

## Database Structure

### Client-Side Database
- Stores user details (name, email, hashed password) for authentication.

### Server-Side Database
- Manages email data with fields for sender, receiver, and message content.

## Workflow

1. **Multiple Clients Interaction**: The server handles simultaneous client connections using threads.
2. **Email Sending**: Clients send emails via the server, which stores them in the database.
3. **Email Retrieval**: Clients fetch emails from the server.
4. **Email Deletion**: Clients request deletion of emails, which the server processes.

## Technologies Used

- **Backend**: Flask, Python, SQLite.
- **Communication**: Socket programming.
- **Security**: Password hashing using `werkzeug`.

## Installation and Usage

### Prerequisites
- Python 3.x installed on your system.

### Steps to Run the Project
1. Clone the repository:
   ```bash
   git clone https://github.com/AdithyaVarma28/Mail-Server/
   cd Mail-Server
   ```
2. Initialize the databases:
   - For the server: A SQLite database `server_messages.db` will be created automatically when the server is run.
   - For the client: Run the following in the project directory:
     ```bash
     python app.py
     ```
     This initializes `database.db`.
3. Start the server:

   ```bash
   python server.py
   ```
4. Run the client application:
   ```bash
   python app.py
   ```
5. Access the client web interface at `http://localhost:5000`.

## Folder Structure

- **server.py**: Contains the server code.
- **app.py**: The client-side Flask application.
- **templates/**: HTML templates for the client web interface (see the GitHub repository for details).