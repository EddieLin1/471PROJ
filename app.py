from flask import Flask, render_template, request, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret"

@app.route("/", methods=["GET"])
def home(): 
    session.clear()
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
                
                return property()
        
        # Return the login page with an error message
        return render_template("Login.html", error="Invalid username or password.")
    
    return render_template('Login.html')

@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return render_template("Login.html")

@app.route("/contractor-view", methods=["GET"])
def contractor():

    with sqlite3.connect("Homeapp.db") as conn:
        emps = conn.execute("SELECT * FROM employee").fetchall()
    
    return render_template("ContractorView.html", emps=emps)

@app.route("/lease-agreement-view", methods=["GET"])
def leaseAgreement():

    with sqlite3.connect("Homeapp.db") as conn:
        las = conn.execute("SELECT * FROM leaseagreement").fetchall()
    
    return render_template("LeaseAgreementView.html", las=las)

@app.route("/property-view", methods=["GET"])
def property():
    if session.get('access') == 'client':
        with sqlite3.connect("Homeapp.db") as conn:
            ps = conn.execute("SELECT * FROM property").fetchall()
    else:
        with sqlite3.connect("Homeapp.db") as conn:
            ps = conn.execute("SELECT * FROM property WHERE OwnerSSN = ?", (session.get('ssn'),)).fetchall()

    return render_template("PropertyView.html", ps=ps)

@app.route("/property-view/<int:property_id>", methods=["GET"])
def property_specific(property_id):
    form = {
        "property_id": 0,
        "property_type": "",
        "address": "",
        "description": "",
        "floor_number": None,
        "num_floors": None
    }
    rs = None

    if property_id != 0:
        with sqlite3.connect("Homeapp.db") as conn:
            p = conn.execute("SELECT * FROM PROPERTY WHERE PropertyID = ?", (property_id,)).fetchone()
            if p:
                form["property_id"] = p[0]
                form["address"] = p[1]
                form["description"] = p[2]

                a = conn.execute("SELECT FloorNumber FROM APARTMENT WHERE PropertyID = ?", (property_id,)).fetchone()
                h = conn.execute("SELECT NumFloors FROM HOUSE WHERE PropertyID = ?", (property_id,)).fetchone()

                if a:
                    form["property_type"] = "apartment"
                    form["floor_number"] = a[0]
                elif h:
                    form["property_type"] = "house"
                    form["num_floors"] = h[0]
            rs = conn.execute("SELECT * FROM ROOM WHERE PropertyID = ?", (property_id,)).fetchall()
    

    return render_template("PropertyEdit.html", form=form, rs=rs)


@app.route("/add-property", methods=["POST"])
def add_property():
    property_id = int(request.form["property_id"])
    property_type = request.form["property_type"]
    address = request.form["address"]
    description = request.form["description"]
    floor_number = request.form.get("floor_number")
    num_floors = request.form.get("num_floors")

    with sqlite3.connect("Homeapp.db") as conn:
        cursor = conn.cursor()

        if property_id == 0:
            # --- ADD NEW ---
            base_id = 4000 if property_type == "apartment" else 5000
            max_id = cursor.execute("""
                SELECT MAX(PropertyID) FROM PROPERTY WHERE PropertyID BETWEEN ? AND ?
            """, (base_id, base_id + 999)).fetchone()[0]
            new_id = (max_id + 1) if max_id else base_id + 1

            cursor.execute("""
                INSERT INTO PROPERTY (PropertyID, Address, Description, OwnerSSN)
                VALUES (?, ?, ?, ?)
            """, (new_id, address, description, session.get('ssn')))

            if property_type == "apartment":
                cursor.execute("INSERT INTO APARTMENT (PropertyID, FloorNumber) VALUES (?, ?)",
                               (new_id, int(floor_number)))
            else:
                cursor.execute("INSERT INTO HOUSE (PropertyID, NumFloors) VALUES (?, ?)",
                               (new_id, int(num_floors)))

        else:
            # --- UPDATE EXISTING ---
            cursor.execute("""
                UPDATE PROPERTY SET Address = ?, Description = ? WHERE PropertyID = ?
            """, (address, description, property_id))

            # Check what type currently exists
            is_apartment = cursor.execute("SELECT 1 FROM APARTMENT WHERE PropertyID = ?", (property_id,)).fetchone()
            is_house = cursor.execute("SELECT 1 FROM HOUSE WHERE PropertyID = ?", (property_id,)).fetchone()

            if property_type == "apartment":
                if is_house:
                    cursor.execute("DELETE FROM HOUSE WHERE PropertyID = ?", (property_id,))
                cursor.execute("REPLACE INTO APARTMENT (PropertyID, FloorNumber) VALUES (?, ?)",
                               (property_id, int(floor_number)))
            else:  # house
                if is_apartment:
                    cursor.execute("DELETE FROM APARTMENT WHERE PropertyID = ?", (property_id,))
                cursor.execute("REPLACE INTO HOUSE (PropertyID, NumFloors) VALUES (?, ?)",
                               (property_id, int(num_floors)))

        conn.commit()

    return property()

@app.route("/property-delete/<int:property_id>", methods=["GET"])
def delete_property(property_id):
    with sqlite3.connect("Homeapp.db") as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM PROPERTY WHERE PropertyID = ?", (property_id,))
        conn.commit()
    
    return property()

@app.route("/test-house", methods=["GET"])
def thouse():

    with sqlite3.connect("Homeapp.db") as conn:
        ths = conn.execute("SELECT * FROM house").fetchall()
    
    return render_template("thouse.html", ths=ths)

@app.route("/test-appt", methods=["GET"])
def tappt():

    with sqlite3.connect("Homeapp.db") as conn:
        tas = conn.execute("SELECT * FROM apartment").fetchall()
    
    return render_template("tappt.html", tas=tas)


if __name__ == '__main__':
    app.run(debug=True)