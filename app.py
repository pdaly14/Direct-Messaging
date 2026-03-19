from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
app = Flask(__name__)
app.secret_key = "supersecretkey"  # needed for sessions


messages = [
        {"user": "Alex", "text": "Hello!", "time": "09:30"},
        {"user": "You", "text": "Hi!", "time": "10:00"},
    ]

users = [
    {
        "username": "You",
        "password": generate_password_hash("password123")
    },
    {
        "username": "Alex",
        "password": generate_password_hash("password123")
    },
    {   "username": "admin", 
     "password": generate_password_hash("admin123") }
]
  


@app.route("/completesignup", methods=["POST"])
def complete_signup():
    username = request.form.get("username")
    password = request.form.get("password")

    if username and password:
        # Check if user already exists
        if not any(user["username"] == username for user in users):
            # Create new user
            users.append({
                "username": username,
                "password": generate_password_hash(password)
            })
            session["username"] = username
            return redirect(url_for("home"))
        else:
            return "Username already exists!"
    else:
        return "Please fill in all fields!"

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if "username" in session:
        return redirect(url_for("home"))  # already logged in
    return render_template("signup.html")
@app.route("/")
def home():
    if "username" not in session:
        return redirect(url_for("login"))  # force login first

    return render_template("index.html", messages=messages, username=session["username"])


@app.route("/send", methods=["POST"])
def send_message():
    if "username" not in session:
        return redirect(url_for("login"))

    msg_text = request.form.get("message")

    if msg_text:
        timestamp = datetime.now().strftime("%H:%M")
        messages.append({
            "user": session["username"],
            "text": msg_text,
            "time": timestamp
        })

    return redirect(url_for("home"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Check if user exists and password is correct
        user = next((u for u in users if u["username"] == username), None)
        if user and check_password_hash(user["password"], password):
            session["username"] = username  # save user in session
            return redirect(url_for("home"))
        else:
            return "Invalid username or password!'"
    return render_template("login.html")

@app.route("/logout", methods=["POST", "GET"])
def logout():
    session.pop("username", None)  # remove user from session
    return redirect(url_for("login"))

@app.route("/profile", methods=["POST", "GET"])
def profile():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("profile.html", username=session["username"])
@app.route("/messages")
def get_messages():
    return messages
@app.route("/secret")
def secret():
   return render_template("about.html")
@app.route("/admin" , methods=["POST", "GET"])
def admin():
    if "username" not in session or session["username"] != "admin":
        return redirect(url_for("login"))
    return render_template("admin.html", users=users, messages=messages)

@app.route("/delete_message/<int:msg_index>", methods=["POST"])
def delete_message(msg_index):
    # Security check: only 'admin' can delete
    if "username" not in session or session["username"] != "admin":
        return redirect(url_for("login"))
    
    # Check if the index exists before trying to pop it
    if 0 <= msg_index < len(messages):
        messages.pop(msg_index)
        
    return redirect(url_for("admin"))


@app.route("/clear_all_messages", methods=["POST"])
def clear_all_messages():
    # Security check: only 'admin' can clear everything
    if "username" not in session or session["username"] != "admin":
        return redirect(url_for("login"))
    
    # This empties the global 'messages' list
    messages.clear()
    
    return redirect(url_for("admin"))


@app.route("/delete_user/<username>", methods=["POST"])
def delete_user(username):
    global users  # This tells Flask to change the MASTER list
    if "username" not in session or session["username"] != "admin":
        return redirect(url_for("login"))
    if username == "admin":
        return "Cannot delete admin user!"
    # Rebuild the list without the deleted user
    users = [u for u in users if u["username"] != username]
    return redirect(url_for("admin"))



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)

