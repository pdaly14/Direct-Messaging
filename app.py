from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
app = Flask(__name__)
app.secret_key = "supersecretkey"  # needed for sessions


messages = [
        {"user": "Alex", "text": "Hello!", "time": "09:30"},
        {"user": "You", "text": "Hi!", "time": "10:00"},
    ]

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
        if username in ["You", "Alex"]:
            session["username"] = username  # save user in session
            return redirect(url_for("home"))
        else:
            return "Invalid username! Use 'You' or 'Alex'"
    return render_template("login.html")

@app.route("/logout", methods=["POST"])
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
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)

