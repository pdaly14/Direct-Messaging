from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"  # needed for sessions
key = "Nantucket"





messages = [
        {"user": "Jonathan", "text": "Hello!", "time": "09:30"},
        {"user": "admin", "text": "Hi!", "time": "10:00"},
    ]

users = [
    {
        "username": "Jonathan",
        "password" : generate_password_hash("password123"),
        "description": "I am gay with Budvin"
    },
    {
        "username": "Nadula",
        "password": generate_password_hash("password123"),
        "description": "I am a student"
    },
    {   "username": "admin", 
     "password": generate_password_hash("admin123"),
     "description": "I am the admin I can cook all of u and eat u all up"
    },
    {   "username": "Budvin",
      "password": generate_password_hash("Budvin"),
      "description": "I am Budvin, gay with Jonathan we have sex all day and night"}   

]
  
@app.before_request
def check_if_user_still_exists():
    if "username" in session:
        # Check if the person in the session is actually in your 'users' list
        exists = any(u["username"] == session["username"] for u in users)
        
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
            if not any(user["username"] == username for user in users):
            # Create new user
                users.append({
                    "username": username,
                    "password": generate_password_hash(password),
                    "description": "No description yet."
                })
                session["username"] = username
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

    return render_template("index.html", messages=messages, username=session["username"], )


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

@app.route("/update_description", methods=["POST"])
def update_description():
    if "username" not in session:
        return redirect(url_for("login"))
    
    new_bio = request.form.get("new_bio")
    current_user = session["username"]
    
    # Update the description for the current user
    for user in users:
        if user["username"] == current_user:
            user["description"] = new_bio
            break
    
    return redirect(url_for("profile", user=current_user))

@app.route("/logout", methods=["POST", "GET"])
def logout():
    session.pop("username", None)  # remove user from session
    return redirect(url_for("login"))

@app.route("/profile/<user>", methods=["POST", "GET"])
def profile(user):
    if "username" not in session:
        return redirect(url_for("login"))
    description = next((u["description"] for u in users if u["username"] == user), "No description available.")
    return render_template("profile.html", profile_name=user, profile_desc=description, current_user=session["username"]   )

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
    return render_template("admin.html", users=users, messages=messages, code=key)

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

@app.route("/changecode/", methods=["POST"])
def change_code():
    if "username" not in session or session["username"] != "admin":
        return redirect(url_for("login"))
    
    global key
    key = request.form.get("code")
    return redirect(url_for("admin"))

if __name__ == '__main__':
      app.run(host="0.0.0.0", port=5000, debug=True)

