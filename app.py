from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        name = request.form["name"]
        with sqlite3.connect("database.db") as conn:
            conn.execute("INSERT INTO users (name) VALUES (?)", (name,))
    
    # Fetch users
    with sqlite3.connect("database.db") as conn:
        users = conn.execute("SELECT * FROM users").fetchall()
    
    return render_template("index.html", users=users)

@app.route("/login", methods=["GET", "POST"])
def desired_route():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "pass":
            return render_template("PropertyView.html")
        
        # Return the login page with an error message
        return render_template("Login.html", error="Invalid username or password.")
    
    return render_template('Login.html')


if __name__ == '__main__':
    app.run(debug=True)