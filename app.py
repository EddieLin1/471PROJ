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
                
                existhomeowner = conn.execute("SELECT SSN FROM HOMEOWNER")
                existhomeowner = list(zip(*existhomeowner))[0]

                existclient = conn.execute("SELECT SSN FROM CLIENT")
                existclient = list(zip(*existclient))[0]

                existemp = conn.execute("SELECT SSN FROM EMPLOYEE")
                existemp = list(zip(*existemp))[0]

                if int(result[0]) in existhomeowner:
                    access = "homeowner"
                elif int(result[0]) in existclient:
                    access = "client"
                elif int(result[0]) in existemp:
                    access = "employee"

#                first_digit = str(result[0])[0]

#                match first_digit:
#                    case '1': 
#                        access = "client"
#                    case '2': 
#                        access = "homeowner"
#                    case '3': 
#                        access = "employee"

                session["access"] = access
                if access == "employee":
                    return service_view()
                return property()
        
        # Return the login page with an error message
        return render_template("Login.html", error="Invalid username or password.")
    
    new=False
    return render_template('Login.html', new=new)

@app.route("/new_account", methods=["GET", "POST"])
def new_account():
    if request.method == "POST":
        ssn = request.form["SSN"]
        username = request.form["username"]
        password = request.form["password"]
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        accounttype = request.form["accounttype"]
        if accounttype == "employee":
            jobtype = request.form["jobtype"]

        with sqlite3.connect("Homeapp.db") as conn:
            cursor = conn.cursor()
            existssn = conn.execute("SELECT SSN FROM person").fetchall()
            existssn = list(zip(*existssn))[0]
#            print(existssn)

            if int(ssn) in existssn:
                return render_template('Login.html', new=True, error="invalid SSN")
            
            cursor.execute("""
                INSERT INTO PERSON (SSN, FirstName, LastName, UserName, Password)
                VALUES (?, ?, ?, ?, ?)
                """, (ssn, firstname, lastname, username, password))

            if accounttype == "homeowner":
                cursor.execute("""
                INSERT INTO HOMEOWNER (SSN)
                VALUES (?)
                """, (ssn,))
                return render_template('Login.html', new=False)
            elif accounttype == "client":
                cursor.execute("""
                INSERT INTO CLIENT (SSN)
                VALUES (?)
                """, (ssn,))
                return render_template('Login.html', new=False)
            elif accounttype == "employee":
                cursor.execute("""
                INSERT INTO EMPLOYEE (SSN, JobType)
                VALUES (?, ?)
                """, (ssn, jobtype,))
                return render_template('Login.html', new=False)
          
    new = True
    return render_template('Login.html', new=new)


@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return render_template("Login.html", new = False)

@app.route("/contractor-view", methods=["GET"])
def contractor():

    with sqlite3.connect("Homeapp.db") as conn:
        emps = conn.execute("SELECT e.SSN, e.JobType, p.FirstName, p.LastName, c.CompanyName FROM employee e INNER JOIN person p ON e.SSN == p.SSN INNER JOIN works_for w ON w.EmployeeSSN = e.SSN INNER JOIN company c ON w.CompanyID = c.CompanyID").fetchall()
    
    return render_template("ContractorView.html", emps=emps)

@app.route("/lease-agreement-view", methods=["GET"])
def leaseAgreement():
    #get lease agreements associated with a user
    with sqlite3.connect("Homeapp.db") as conn:
        las = conn.execute("SELECT l.LeaseID, l.StartDate, l.EndDate, l.PropertyID, l.RoomID, l.OwnerSSN, p2.FirstName, p2.LastName, l.ClientSSN, p1.FirstName, p1.LastName FROM leaseagreement AS l INNER JOIN person AS p1 ON l.ClientSSN = p1.SSN INNER JOIN person as p2 ON l.OwnerSSN = p2.SSN WHERE OwnerSSN = ? UNION SELECT l.LeaseID, l.StartDate, l.EndDate, l.PropertyID, l.RoomID, l.OwnerSSN, p2.FirstName, p2.LastName, l.ClientSSN, p1.FirstName, p1.LastName FROM leaseagreement AS l INNER JOIN person AS p1 ON l.ClientSSN = p1.SSN INNER JOIN person as p2 ON l.OwnerSSN = p2.SSN WHERE ClientSSN = ?", (session.get('ssn'), session.get('ssn'),)).fetchall()
    
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
        "property_ID": 0,
        "room_ID": 0,
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
                form["property_ID"] = l[3]
                form["room_ID"] = l[4]
                form["clientSSN"] = l[6]
    
    #return page
    return render_template("LeaseAgreementEdit.html", form=form)
            

@app.route("/add-leaseagreement", methods=["POST"])
def add_leaseagreement():
    #get new/updated values from html form
    lease_id = int(request.form["leaseID"])
    start_date = request.form["start_date"]
    end_date = request.form["end_date"]
    property_ID = request.form["property_ID"]
    room_ID = request.form["room_ID"]
    clientSSN = request.form["clientSSN"]

    #reinitialize form to display to let user retry
    form = {
        "leaseID": lease_id,
        "startDate": start_date,
        "endDate": end_date,
        "property_ID": property_ID,
        "room_ID": room_ID,
        "clientSSN": clientSSN
    }

    with sqlite3.connect("Homeapp.db") as conn:
        cursor = conn.cursor()

        # get existing users
        existuser = conn.execute("SELECT * FROM CLIENT").fetchall()
        existuser = list(zip(*existuser))[0]

        existpropertyroom = conn.execute("SELECT PropertyID, RoomID FROM ROOM").fetchall()
        existproperty = list(zip(*existpropertyroom))[0]

        #check to see that the inputted client is valid
        if int(clientSSN) not in existuser:
            return render_template("LeaseAgreementEdit.html", form=form, error="invalid client SSN")
        #check to see that the inputted date range is valid
        elif start_date > end_date:
            return render_template("LeaseAgreementEdit.html", form=form, error="Invalid date range: the end date cannot be earlier than the start date")
        #check to see if property exists
        elif int(property_ID) not in existproperty:
            return render_template("LeaseAgreementEdit.html", form=form, error="property does not exist")
        #check to see if property and room pair exist
        elif (int(property_ID), int(room_ID)) not in existpropertyroom:
            return render_template("LeaseAgreementEdit.html", form=form, error="room does not exist")

        #get existing leases for propertys and rooms, with their start and end dates
        existlease = conn.execute("SELECT PropertyID, RoomID, StartDate, EndDate FROM leaseagreement").fetchall()

        #iterate through existing leases
        for lease in existlease:
            #if the property and lease are the same as form and also the date range overlaps
            if (int(property_ID), int(room_ID)) == (lease[0], lease[1]) and start_date < lease[3] and end_date > lease[2]:
                #return error message
                return render_template("LeaseAgreementEdit.html", form=form, error="lease already exists for this room")

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
                INSERT INTO LEASEAGREEMENT (LeaseID, StartDate, EndDate, PropertyID, RoomID, OwnerSSN, ClientSSN)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (new_id, start_date, end_date, property_ID, room_ID, session.get('ssn'), clientSSN))

        else:
            # --- UPDATE EXISTING ---
            cursor.execute("""
                UPDATE LEASEAGREEMENT SET StartDate = ?, EndDate = ?, Property_ID = ?, RoomID = ?, ClientSSN = ? WHERE LeaseID = ?
            """, (start_date, end_date, property_ID, room_ID, clientSSN, lease_id))

        conn.commit()

    #reutnr to lease agreement view page
    return leaseAgreement()

@app.route("/leaseagreement-delete/<int:leaseID>", methods=["GET"])
def delete_leaseagreement(leaseID):
    #delete specified leaseId from lease agreement table
    with sqlite3.connect("Homeapp.db") as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM LEASEAGREEMENT WHERE LeaseID = ?", (leaseID,))
        conn.commit()
    
    #return to lease agreement view page
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

@app.route("/property-view-personal", methods=["GET"])
def property_personal():
    with sqlite3.connect("Homeapp.db") as conn:
        ps = conn.execute("SELECT * FROM property p INNER JOIN leaseagreement l ON p.PropertyID = l.PropertyID WHERE l.CLientSSN = ?", (session.get('ssn'),)).fetchall()
    return render_template("PropertyView.html", ps=ps, personal=True)

@app.route("/property-view-personal/<int:property_id>", methods=["GET"])
def property_specific_personal(property_id):
    form = {
        "property_id": 0,
        "property_type": "",
        "address": "",
        "description": "",
        "floor_number": None,
        "num_floors": None
    }
    rs = None

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
            rs = conn.execute("SELECT * FROM ROOM r JOIN LEASEAGREEMENT l ON r.PropertyID = l.PropertyID AND r.RoomID = l.RoomID WHERE r.PropertyID = ? AND l.ClientSSN = ?", (property_id, session.get('ssn'))).fetchall()

    return render_template("PropertyEdit.html", form=form, rs=rs, personal=True)

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
                rs = conn.execute("""
                            SELECT r.*, 
                                EXISTS (
                                    SELECT 1 FROM REQUESTS req 
                                    WHERE req.PropertyID = r.PropertyID 
                                        AND req.RoomID = r.RoomID
                                ) AS HasRequest
                            FROM ROOM r
                            WHERE r.PropertyID = ?
                        """, (property_id,)).fetchall()
                print(rs)

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


@app.route("/room-view/<int:propertyID>/<int:roomID>", methods=["GET"])
def room_specific(propertyID, roomID):
    #initialize form values
    form = {
        "property_ID": propertyID,
        "room_ID": 0,
        "condition": "" 
    }
    #initilize employee list for room
    es = None

    #if not asking for a new room, retrieve attributes of a specific room based on ids
    if roomID != 0:
        with sqlite3.connect("Homeapp.db") as conn:
            l = conn.execute("SELECT * FROM ROOM WHERE PropertyID = ? AND RoomID = ?", (propertyID, roomID, )).fetchone()
            if l:
                form["room_ID"] = l[1]
                form["condition"] = l[2]
            #get employees working on the room
            es = conn.execute("SELECT * FROM WORKS_ON INNER JOIN EMPLOYEE ON WORKS_ON.ESSN = EMPLOYEE.SSN INNER JOIN PERSON ON EMPLOYEE.SSN = PERSON.SSN WHERE PropertyID = ? AND RoomID = ?", (propertyID, roomID, )).fetchall()
            print(es)
    #return page
    return render_template("RoomEdit.html", form=form, es=es)

@app.route("/add-room", methods=["POST"])
def add_room():
    #retrive values from the form to update/add room
    property_ID = int(request.form["property_ID"])
    room_ID = int(request.form["room_ID"])
    condition = request.form["condition"]


    with sqlite3.connect("Homeapp.db") as conn:
        cursor = conn.cursor()

        if room_ID == 0:
            # --- ADD NEW ---
            base_id = 0
            # Find the first unused ID in the range 0 - 1000
            existing_ids = cursor.execute("""
                SELECT RoomID FROM ROOM WHERE PropertyID = ? AND RoomID BETWEEN ? AND ? ORDER BY RoomID
            """, (property_ID, base_id + 1, base_id + 999)).fetchall()

            existing_ids_set = {row[0] for row in existing_ids}
            for candidate_id in range(base_id + 1, base_id + 1000):
                if candidate_id not in existing_ids_set:
                    new_id = candidate_id
                    break

            #insert new lease agreement
            cursor.execute("""
                INSERT INTO ROOM (PropertyID, RoomID, Condition)
                VALUES (?, ?, ?)
            """, (property_ID, new_id, condition))

        else:
            # --- UPDATE EXISTING ---
            cursor.execute("""
                UPDATE ROOM SET Condition = ? WHERE PropertyID = ? AND RoomID = ?
            """, (condition, property_ID, room_ID))

        conn.commit()
    
        if session.get('access') == 'employee':
            return service_view()
        
    #return specific property view page
    return property_specific(property_ID)

@app.route("/room-delete/<int:propertyID>/<int:roomID>", methods=["GET"])
def delete_room(propertyID, roomID):
    #delete room based on specified roomID and propertyID
    with sqlite3.connect("Homeapp.db") as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ROOM WHERE PropertyID = ? AND RoomID = ?", (propertyID, roomID, ))
        conn.commit()
    #return specific property view page
    return property_specific(propertyID)

@app.route("/room-add-employee/<int:propertyID>/<int:roomID>", methods=["POST"])
def add_employee(propertyID, roomID):
    #add employee to work on room
    #retrieve values from form
    property_ID = int(request.form["property_ID"])
    room_ID = int(request.form["room_ID"])
    condition = request.form["condition"]
    emp_SSN = request.form["ESSN"]

    #initialize form values to return to user to retry on error
    form = {
        "property_ID": property_ID,
        "room_ID": room_ID,
        "condition": condition,
        "ESSN": emp_SSN
    }
    #initialize employee list to return to user on error
    es = None

    with sqlite3.connect("Homeapp.db") as conn:
        cursor = conn.cursor()

        #get existing employees
        existemp = conn.execute("SELECT * FROM EMPLOYEE").fetchall()
        existemp = list(zip(*existemp))[0]

        #get list of employees currently working on a room
        es = conn.execute("SELECT * FROM WORKS_ON INNER JOIN EMPLOYEE ON WORKS_ON.ESSN = EMPLOYEE.SSN WHERE PropertyID = ? AND RoomID = ?", (propertyID, roomID, )).fetchall()

        #check to see that the inputted client is valid
        if int(emp_SSN) not in existemp:
            return render_template("RoomEdit.html", form=form, es=es, error="invalid employee SSN")
        
        #check to see if employee is already working on a room
        existworks = conn.execute("SELECT * FROM WORKS_ON WHERE PropertyID = ? AND RoomID = ?", (propertyID, roomID, )).fetchall()
        if existworks:
            existworks = list(zip(*existworks))[2]
            if int(emp_SSN) in existworks:
                return render_template("RoomEdit.html", form=form, es=es, error="employee already works on this room")
        
        #add new employee
        cursor.execute("""
                INSERT INTO WORKS_ON (PropertyID, RoomID, ESSN)
                VALUES (?, ?, ?)
            """, (property_ID, room_ID, emp_SSN))
    #return specific room view page    
    return room_specific(propertyID, roomID)

@app.route("/room-delete-employee/<int:propertyID>/<int:roomID>/<int:ESSN>", methods=["GET"])
def delete_employee(propertyID, roomID, ESSN):
    #remove working employee from room
    with sqlite3.connect("Homeapp.db") as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM WORKS_ON WHERE PropertyID = ? AND RoomID = ? AND ESSN = ?", (propertyID, roomID, ESSN, ))
        conn.commit()
    #return specific room view page
    return room_specific(propertyID, roomID)


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
            WHERE w.ESSN = ?
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

@app.route("/my-requests", methods=["GET"])
def my_request_view():
    if session.get('access') == 'homeowner':
        with sqlite3.connect("Homeapp.db") as conn:
            requests = conn.execute("SELECT r.PropertyID, r.RoomID, r.ClientSSN, per2.FirstName, per2.LastName FROM REQUESTS r INNER JOIN PROPERTY p ON p.PropertyID = r.PropertyID INNER JOIN PERSON per1 ON p.OwnerSSN = per1.SSN INNER JOIN PERSON per2 ON r.ClientSSN = per2.SSN WHERE OwnerSSN = ?", (session.get('ssn'),)).fetchall()
    else:
        with sqlite3.connect("Homeapp.db") as conn:
            requests = conn.execute("SELECT r.PropertyID, r.RoomID, p.OwnerSSN, per1.FirstName, per1.LastName FROM REQUESTS r INNER JOIN PROPERTY p ON p.PropertyID = r.PropertyID INNER JOIN PERSON per1 ON p.OwnerSSN = per1.SSN INNER JOIN PERSON per2 ON r.ClientSSN = per2.SSN WHERE ClientSSN = ?", (session.get('ssn'),)).fetchall()

    print(requests)
    return render_template("RequestView.html", requests=requests)

@app.route("/my-requests-delete/<int:property_id>/<int:room_id>/<int:client_ssn>", methods=["GET"])
def my_request_delete(property_id, room_id, client_ssn):
    with sqlite3.connect("Homeapp.db") as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("DELETE FROM REQUESTS WHERE PropertyID = ? AND RoomID = ? AND ClientSSN = ?", (property_id, room_id, client_ssn))
        conn.commit()
    return my_request_view()

@app.route("/add-request/<int:property_id>/<int:room_id>", methods=["GET"])
def add_request(property_id, room_id):

    with sqlite3.connect("Homeapp.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
                    INSERT INTO REQUESTS (PropertyID, RoomID, ClientSSN)
                    VALUES (?, ?, ?)
                """, (property_id, room_id, session.get('ssn')))
    return my_request_view()

if __name__ == '__main__':
    app.run(debug=True)