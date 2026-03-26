from typing import List
from unittest.mock import Base

from flask import Flask, jsonify, render_template, request, redirect, url_for, session
from sqlalchemy import create_engine, Column, Integer, String, text
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.orm import declarative_base, sessionmaker
Base = declarative_base()
app = Flask(__name__)
app.secret_key = "supersecretkey"  # needed for sessions
key = "Nantucket"





engine = create_engine('sqlite:///example.db')
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(20), unique=True)
    password = Column(String(20)) 
    description = Column(String(200)) 
    pfp =  Column(String(200))



class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    user = Column(String(20))
    text = Column(String(200))
    time = Column(String(10))

Base.metadata.create_all(engine)
Session = sessionmaker(engine)
db_session = Session()

messages = [
        {"user": "Jonathan", "text": "Hello!", "time": "09:30"},
        {"user": "admin", "text": "Hi!", "time": "10:00"},
    ]

users = [
    {
        "username": "Jonathan",
        "password" : generate_password_hash("password123"),
        "description": "I am gay with Budvin",
        "pfp": ""
    },
    {
        "username": "Nadula",
        "password": generate_password_hash("password123"),
        "description": "I am a student",
        "pfp": ""
    },
    {   "username": "admin", 
     "password": generate_password_hash("admin123"),
     "description": "I am the admin I can cook all of u and eat u all up",
     "pfp": ""
    },
    {   "username": "Budvin",
      "password": generate_password_hash("Budvin"),
      "description": "I am Budvin, gay with Jonathan we have sex all day and night",
      "pfp": ""
    }
    
]


def seed_users():
    for user in users:
        existing_user = db_session.query(User).filter_by(username=user["username"]).first()
        if not existing_user:
            new_user = User(username=user["username"], password=user["password"], description=user["description"], pfp=user["pfp"])
            db_session.add(new_user)

def seed_messages():
    for msg in messages:
        existing_msg = db_session.query(Message).filter_by(user=msg["user"], text=msg["text"], time=msg["time"]).first()
        if not existing_msg:
            new_msg = Message(user=msg["user"], text=msg["text"], time=msg["time"])
            db_session.add(new_msg)

seed_users()
seed_messages()
db_session.commit()

@app.before_request
def check_if_user_still_exists():
    if "username" in session:
        # Check if the person in the session is actually in your 'users' list
        exists = db_session.query(User).filter_by(username=session["username"]).first() is not None
        
        if not exists:
            session.clear()  # Kick them out!
            return redirect(url_for("login"))


@app.route("/completesignup", methods=["POST"])
def complete_signup():
    username = request.form.get("username")
    password = request.form.get("password")
    code = request.form.get("accesskey")

    if code == key:
        if username and password and code:
        # Check if user already exists
            if not db_session.query(User).filter_by(username=username).first():

            # Create new user
                users.append({
                    "username": username,
                    "password": generate_password_hash(password),
                    "description": "No description yet."
                })
                new_user = User(
                    username=username,
                    password=generate_password_hash(password),
                    description="No description yet."
                )
                try:
                    db_session.add(new_user)
                    db_session.commit()
                except:
                    db_session.rollback()
                    return "Username already exists!"
                return redirect(url_for("home"))
            else:
                return "Username already exists!"
        else:
            return "Please fill in all fields!"
    else:
        return "Incorrect secret code"
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if "username" in session:
        return redirect(url_for("home"))  # already logged in
    return render_template("signup.html", code=key)
@app.route("/")
def home():
    if "username" not in session:
        return redirect(url_for("login"))  # force login first
    messages = db_session.query(Message).all()
    return render_template("index.html", messages=messages, username=session["username"], )


@app.route("/send", methods=["POST"])
def send_message():
    if "username" not in session:
        return redirect(url_for("login"))

    msg_text = request.form.get("message")

    if msg_text:
        timestamp = datetime.now().strftime("%H:%M")
        new_message = Message(
            user=session["username"],
            text=msg_text,
            time=timestamp
        )
        db_session.add(new_message)
        db_session.commit()

    return redirect(url_for("home"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Check if user exists and password is correct
        user = db_session.query(User).filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["username"] = username  # save user in session
            return redirect(url_for("home"))
        else:
            return "Invalid username or password!"
    return render_template("login.html")

@app.route("/update_description", methods=["POST"])
def update_description():
    if "username" not in session:
        return redirect(url_for("login"))
    
    new_bio = request.form.get("new_bio")
    current_user = session["username"]
    
    # Update the description for the current user
    user = db_session.query(User).filter_by(username=current_user).first()
    if user:
        db_session.query(User).filter_by(username=current_user).update({"description": new_bio})
        db_session.commit()
    
    return redirect(url_for("profile", user=current_user))

@app.route("/logout", methods=["POST", "GET"])
def logout():
    session.pop("username", None)  # remove user from session
    return redirect(url_for("login"))

@app.route("/profile/<user>", methods=["POST", "GET"])
def profile(user):
    if "username" not in session:
        return redirect(url_for("login"))
    description = db_session.query(User).filter_by(username=user).first().description
    return render_template("profile.html", profile_name=user, profile_desc=description, current_user=session["username"]   )

@app.route("/messages")
def get_messages():
    mesagges = []
    for msg in db_session.query(Message).all():
        mesagges.append({
            "user": msg.user,
            "text": msg.text,
            "time": msg.time
        })

    return jsonify(mesagges)
@app.route("/secret")
def secret():
   return render_template("about.html")
@app.route("/admin" , methods=["POST", "GET"])
def admin():
    if "username" not in session or session["username"] != "admin":
        return redirect(url_for("login"))
    users = db_session.query(User).all()
    messages = db_session.query(Message).all()
   
    return render_template("admin.html", users=users, messages=messages, code=key)

@app.route("/delete_message/<int:msg_index>", methods=["POST"])
def delete_message(msg_index):
    # Security check: only 'admin' can delete
    if "username" not in session or session["username"] != "admin":
        return redirect(url_for("login"))
    
    # Check if the index exists before trying to pop it
    if 0 <= msg_index < db_session.query(Message).count():
        message_to_delete = db_session.query(Message).offset(msg_index).first()
        db_session.delete(message_to_delete)
        db_session.commit()
        
    return redirect(url_for("admin"))


@app.route("/clear_all_messages", methods=["POST"])
def clear_all_messages():
    # Security check: only 'admin' can clear everything
    if "username" not in session or session["username"] != "admin":
        return redirect(url_for("login"))
    
    # This empties the global 'messages' list
    db_session.query(Message).delete()
    db_session.commit()
    
    return redirect(url_for("admin"))


@app.route("/delete_user/<username>", methods=["POST"])
def delete_user(username):
    global users  # This tells Flask to change the MASTER list
    if "username" not in session or session["username"] != "admin":
        return redirect(url_for("login"))
    if username == "admin":
        return "Cannot delete admin user!"
    # Rebuild the list without the deleted user
    db_session.query(User).filter_by(username=username).delete()
    db_session.commit()
    return redirect(url_for("admin"))

@app.route("/changecode/", methods=["POST"])
def change_code():
    if "username" not in session or session["username"] != "admin":
        return redirect(url_for("login"))
    
    global key
    key = request.form.get("code")
    return redirect(url_for("admin"))

if __name__ == '__main__':
      app.run(host="127.0.0.1", port=5000, debug=True)

