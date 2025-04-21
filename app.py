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
                if access == "employee":
                    return service_view()
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
    #get lease agreements associated with a user
    with sqlite3.connect("Homeapp.db") as conn:
        las = conn.execute("SELECT * FROM leaseagreement WHERE OwnerSSN = ? UNION SELECT * FROM leaseagreement WHERE ClientSSN = ?", (session.get('ssn'), session.get('ssn'),)).fetchall()
    
    #check permissions
    if session.get('access') == "homeowner":
        addremoveView = True
    else:
        addremoveView = False

    return render_template("LeaseAgreementView.html", las=las, permission=addremoveView)

@app.route("/lease-agreement-view/<int:leaseID>", methods=["GET"])
def leaseagreement_specific(leaseID):
    #initialize form values
    form = {
        "leaseID": 0,
        "startDate": 0,
        "endDate": 0,
        "clientSSN": 0,
    }

    #if not asking for a new lease agreement, retrieve attributes of a specific lease agreement based on id
    if leaseID != 0:
        with sqlite3.connect("Homeapp.db") as conn:
            l = conn.execute("SELECT * FROM leaseagreement WHERE LeaseID = ?", (leaseID, )).fetchone()
            if l:
                form["leaseID"] = l[0]
                form["startDate"] = l[1]
                form["endDate"] = l[2]
                form["clientSSN"] = l[4]
    
    #return page
    return render_template("LeaseAgreementEdit.html", form=form)
            

@app.route("/add-leaseagreement", methods=["POST"])
def add_leaseagreement():
    #get new/updated values from html form
    lease_id = int(request.form["leaseID"])
    start_date = request.form["start_date"]
    end_date = request.form["end_date"]
    clientSSN = request.form["clientSSN"]

    form = {
        "leaseID": lease_id,
        "startDate": start_date,
        "endDate": end_date,
        "clientSSN": clientSSN
    }

    with sqlite3.connect("Homeapp.db") as conn:
        cursor = conn.cursor()

        # get existing users
        existuser = conn.execute("SELECT * FROM CLIENT").fetchall()
        existuser = list(zip(*existuser))[0]

        #check to see that the inputted client is valid
        if int(clientSSN) not in existuser:
            return render_template("LeaseAgreementEdit.html", form=form, error="invalid client SSN")
        #check to see that the inputted date range is valid
        elif start_date > end_date:
            return render_template("LeaseAgreementEdit.html", form=form, error="Invalid date range: the end date cannot be earlier than the start date")

        if lease_id == 0:
            # --- ADD NEW ---
            base_id = 6000
            # Find the first unused ID in the range 6000-69999
            existing_ids = cursor.execute("""
                SELECT LeaseID FROM LEASEAGREEMENT WHERE LeaseID BETWEEN ? AND ? ORDER BY LeaseID
            """, (base_id + 1, base_id + 999)).fetchall()

            existing_ids_set = {row[0] for row in existing_ids}
            for candidate_id in range(base_id + 1, base_id + 1000):
                if candidate_id not in existing_ids_set:
                    new_id = candidate_id
                    break

            #insert new lease agreement
            cursor.execute("""
                INSERT INTO LEASEAGREEMENT (LeaseID, StartDate, EndDate, OwnerSSN, ClientSSN)
                VALUES (?, ?, ?, ?, ?)
            """, (new_id, start_date, end_date, session.get('ssn'), clientSSN))

        else:
            # --- UPDATE EXISTING ---
            cursor.execute("""
                UPDATE LEASEAGREEMENT SET StartDate = ?, EndDate = ?, ClientSSN = ? WHERE LeaseID = ?
            """, (start_date, end_date, clientSSN, lease_id))

        conn.commit()

    return leaseAgreement()

@app.route("/leaseagreement-delete/<int:leaseID>", methods=["GET"])
def delete_leaseagreement(leaseID):
    with sqlite3.connect("Homeapp.db") as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM LEASEAGREEMENT WHERE LeaseID = ?", (leaseID,))
        conn.commit()
    
    return leaseAgreement()


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
            # Find the first unused ID in the range 4001–4999 or 5001–5999
            existing_ids = cursor.execute("""
                SELECT PropertyID FROM PROPERTY WHERE PropertyID BETWEEN ? AND ? ORDER BY PropertyID
            """, (base_id + 1, base_id + 999)).fetchall()

            existing_ids_set = {row[0] for row in existing_ids}
            for candidate_id in range(base_id + 1, base_id + 1000):
                if candidate_id not in existing_ids_set:
                    new_id = candidate_id
                    break

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


@app.route("/service-view", methods=["GET"])
def service_view():
    with sqlite3.connect("Homeapp.db") as conn:
        ssn = session.get("ssn")
        query = """
            SELECT r.PropertyID, r.RoomID, r.Condition, p.Address
            FROM ROOM r
            INNER JOIN WORKS_ON w ON r.PropertyID = w.PropertyID AND r.RoomID = w.RoomID
            INNER JOIN PROPERTY p ON r.PropertyID = p.PropertyID
            WHERE r.Condition != 'Excellent' AND w.ESSN = ?
        """
        services = conn.execute(query, (ssn,)).fetchall()
    return render_template("ServiceView.html", services=services)

# --- Delete WORKS_ON route ---
@app.route("/delete-workson/<int:property_id>/<int:room_id>", methods=["GET"])
def delete_workson(property_id, room_id):
    ssn = session.get("ssn")
    with sqlite3.connect("Homeapp.db") as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("DELETE FROM WORKS_ON WHERE PropertyID = ? AND RoomID = ? AND ESSN = ?", (property_id, room_id, ssn))
        conn.commit()
    return service_view()

if __name__ == '__main__':
    app.run(debug=True)