from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home(): 
    return render_template("index.html")

@app.route("/user", methods=["GET", "POST"])
def user():
    if request.method == "POST":
        name = request.form["name"]
        with sqlite3.connect("Homeapp.db") as conn:
            conn.execute("INSERT INTO person (name) VALUES (?)", (name,))
    
    # Fetch users
    with sqlite3.connect("Homeapp.db") as conn:
        users = conn.execute("SELECT * FROM person").fetchall()
    
    return render_template("UserView.html", users=users)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "pass":
            return render_template("PropertyView.html")
        
        # Return the login page with an error message
        return render_template("Login.html", error="Invalid username or password.")
    
    return render_template('Login.html')

@app.route("/contractor-view", methods=["GET"])
def contractor():
    # Fetch employees
    with sqlite3.connect("Homeapp.db") as conn:
        emps = conn.execute("SELECT * FROM employee").fetchall()
    
    return render_template("ContractorView.html", emps=emps)

@app.route("/lease-agreement-view", methods=["GET"])
def leaseAgreement():
    # Fetch employees
    with sqlite3.connect("Homeapp.db") as conn:
        las = conn.execute("SELECT * FROM leaseagreement").fetchall()
    
    return render_template("LeaseAgreementView.html", las=las)

@app.route("/property-view", methods=["GET"])
def property():
    # Fetch employees
    with sqlite3.connect("Homeapp.db") as conn:
        ps = conn.execute("SELECT * FROM property").fetchall()
    
    return render_template("PropertyView.html", ps=ps)

@app.route("/room-view", methods=["GET"])
def room():
    # Fetch employees
    with sqlite3.connect("Homeapp.db") as conn:
        rs = conn.execute("SELECT * FROM room").fetchall()
    
    return render_template("RoomView.html", rs=rs)


if __name__ == '__main__':
    app.run(debug=True)