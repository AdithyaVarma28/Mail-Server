from flask import Flask,request,render_template,redirect,url_for,flash
import sqlite3
import socket
from werkzeug.security import generate_password_hash,check_password_hash
from flask import jsonify


app=Flask(__name__)
app.secret_key='API_KEY'

HOST="HOST_IP"
PORT=6969

def init_db():
    conn=sqlite3.connect('database.db')
    cursor=conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_email TEXT NOT NULL,
            receiver_email TEXT NOT NULL,
            message TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_email',methods=['GET','POST'])
def send_email():
    if request.method=='POST':
        sender_email=request.form['sender_email']
        receiver_email=request.form['receiver_email']
        message=request.form['message']
        try:
            response=send_to_server(f"SEND_EMAIL|{sender_email}|{receiver_email}|{message}")
            if "successfully" in response.lower():
                flash('Email sent successfully!','success')
            else:
                flash(f"Failed to send email: {response}",'danger')
        except Exception as e:
            flash(f"Error: {str(e)}",'danger')
        return redirect(url_for('send_email'))
    return render_template('send_email.html')

@app.route('/retrieve_email',methods=['GET','POST'])
def retrieve_email():
    emails=[]  
    if request.method=='POST':
        user_email=request.form['email']
        try:
            response=send_to_server(f"REQUEST_EMAILS|{user_email}")
            if response.startswith("EMAIL_DATA"):
                messages=response.split("\n")
                for message in messages:
                    if message.startswith("EMAIL_DATA"):
                        _,sender,receiver,content=message.split("|",3)
                        emails.append({'sender':sender,'receiver':receiver,'message':content})
            else:
                flash(response,'warning')
        except Exception as e:
            flash(f"Error: {str(e)}",'danger')
    return render_template('retrieve_email.html',emails=emails)

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']
        conn=sqlite3.connect('database.db')
        cursor=conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email=?',(email,))
        user=cursor.fetchone()
        conn.close()
        if user and check_password_hash(user[3],password): 
            flash('Login successful!','success')
            return redirect(url_for('send_email'))
        else:
            flash('Invalid email or password','danger')
    return render_template('login.html')

@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method=='POST':
        name=request.form['name']
        email=request.form['email']
        password=request.form['password']
        hashed_password=generate_password_hash(password)
        conn=sqlite3.connect('database.db')
        cursor=conn.cursor()
        try:
            cursor.execute('INSERT INTO users (name,email,password) VALUES (?,?,?)', 
                           (name,email,hashed_password))
            conn.commit()
            flash('Account created successfully!','success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already exists','danger')
        finally:
            conn.close()
    return render_template('signup.html')

@app.route('/delete_email',methods=['POST'])
def delete_email():
    if request.method=='POST':
        receiver=request.form['receiver']
        try:
            response=send_to_server(f"DELETE_EMAILS|{receiver}")
            return jsonify({'status':'success','message':response})
        except Exception as e:
            return jsonify({'status':'error','message':str(e)}),500

@app.route('/exit',methods=['GET'])
def exit_app():
    send_to_server("DISCONNECT")
    return "<h1>Exited Successfully!</h1>"

def send_to_server(message):
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as client_socket:
        client_socket.settimeout(5)  
        client_socket.connect((HOST,PORT))
        client_socket.sendall(message.encode())
        response = client_socket.recv(1024).decode() 
    return response

if __name__=='__main__':
    init_db()
    app.run(debug=True)