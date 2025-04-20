from flask import Flask, render_template, request, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret"

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

        with sqlite3.connect("Homeapp.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM PERSON WHERE UserName = ? AND Password = ?", (username, password))
            result = cursor.fetchone()
            ps = conn.execute("SELECT * FROM property").fetchall()
            
            #setting permission getting SSN and permission access in session variable
            if result:
                #store name and access for login page and permissions
                session['ssn'] = result[0]
                session['name'] = result[1] + ' ' + result[2]
                first_digit = str(result[0])[0]

                match first_digit:
                    case '1': 
                        access = "client"
                    case '2': 
                        access = "homeowner"
                    case '3': 
                        access = "employee"

                session["access"] = access
                
                return render_template("PropertyView.html", ps=ps)
        
        # Return the login page with an error message
        return render_template("Login.html", error="Invalid username or password.")
    
    return render_template('Login.html')

@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return render_template("Login.html")

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

@app.route("/edit", methods=["GET"])
def edit():
    return render_template("edit.html")

if __name__ == '__main__':
    app.run(debug=True)