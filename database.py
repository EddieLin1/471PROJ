import sqlite3

def init_db():
    conn = sqlite3.connect("Homeapp.db")
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS PERSON (
        SSN INTEGER PRIMARY KEY,
        FirstName TEXT NOT NULL,
        LastName TEXT,
        UserName TEXT UNIQUE,
        Password TEXT
    );

    CREATE TABLE IF NOT EXISTS CLIENT (
        SSN INTEGER PRIMARY KEY,
        FOREIGN KEY (SSN) REFERENCES PERSON(SSN)
        ON DELETE CASCADE
        ON UPDATE CASCADE
    );

    CREATE TABLE IF NOT EXISTS HOMEOWNER (
        SSN INTEGER PRIMARY KEY,
        FOREIGN KEY (SSN) REFERENCES PERSON(SSN)
        ON DELETE CASCADE
        ON UPDATE CASCADE
    );

    CREATE TABLE IF NOT EXISTS EMPLOYEE (
        SSN INTEGER PRIMARY KEY,
        JobType TEXT,
        FOREIGN KEY (SSN) REFERENCES PERSON(SSN)
        ON DELETE CASCADE
        ON UPDATE CASCADE
    );

    CREATE TABLE IF NOT EXISTS COMPANY (
        CompanyID INTEGER PRIMARY KEY,
        CompanyName TEXT,
        CompanyType TEXT
    );

    CREATE TABLE IF NOT EXISTS PROPERTY (
        PropertyID INTEGER PRIMARY KEY,
        Address TEXT NOT NULL,
        Description TEXT,
        OwnerSSN INTEGER,
        FOREIGN KEY (OwnerSSN) REFERENCES HOMEOWNER(SSN)
        ON DELETE CASCADE
        ON UPDATE CASCADE
    );

    CREATE TABLE IF NOT EXISTS APARTMENT (
        PropertyID INTEGER PRIMARY KEY,
        FloorNumber INTEGER,
        FOREIGN KEY (PropertyID) REFERENCES PROPERTY(PropertyID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
    );

    CREATE TABLE IF NOT EXISTS HOUSE (
        PropertyID INTEGER PRIMARY KEY,
        NumFloors INTEGER,
        FOREIGN KEY (PropertyID) REFERENCES PROPERTY(PropertyID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
    );

    CREATE TABLE IF NOT EXISTS LEASEAGREEMENT (
        LeaseID INTEGER PRIMARY KEY,
        StartDate TEXT,
        EndDate TEXT,
        OwnerSSN INTEGER NOT NULL,
        ClientSSN INTEGER NOT NULL,
        FOREIGN KEY (OwnerSSN) REFERENCES HOMEOWNER(SSN)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
        FOREIGN KEY (ClientSSN) REFERENCES CLIENT(SSN)
        ON DELETE CASCADE
        ON UPDATE CASCADE
    );

    CREATE TABLE IF NOT EXISTS ROOM (
        PropertyID INTEGER,
        RoomNumber INTEGER,
        Condition TEXT,
        LeaseID INTEGER,
        PRIMARY KEY (PropertyID, RoomNumber),
        FOREIGN KEY (PropertyID) REFERENCES PROPERTY(PropertyID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
        FOREIGN KEY (LeaseID) REFERENCES LEASEAGREEMENT(LeaseID)
        ON DELETE NO ACTION
        ON UPDATE CASCADE
    );

    CREATE TABLE IF NOT EXISTS WORKS_FOR (
        EmployeeSSN INTEGER,
        CompanyID INTEGER,
        PRIMARY KEY (EmployeeSSN, CompanyID),
        FOREIGN KEY (EmployeeSSN) REFERENCES EMPLOYEE(SSN)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
        FOREIGN KEY (CompanyID) REFERENCES COMPANY(CompanyID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
    );

    CREATE TABLE IF NOT EXISTS WORKS_ON (
        PropertyID INTEGER,
        ESSN INTEGER,
        PRIMARY KEY (PropertyID, ESSN),
        FOREIGN KEY (PropertyID) REFERENCES PROPERTY(PropertyID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
        FOREIGN KEY (ESSN) REFERENCES EMPLOYEE(SSN)
        ON DELETE CASCADE
        ON UPDATE CASCADE
    );

    CREATE TABLE IF NOT EXISTS RENTS (
        PropertyID INTEGER,
        RoomNumber INTEGER,
        ClientSSN INTEGER,
        PRIMARY KEY (PropertyID, RoomNumber, ClientSSN),
        FOREIGN KEY (PropertyID, RoomNumber) REFERENCES ROOM(PropertyID, RoomNumber)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
        FOREIGN KEY (ClientSSN) REFERENCES CLIENT(SSN)
        ON DELETE CASCADE
        ON UPDATE CASCADE
    );
    """)

    conn.commit()
    conn.close()

def insert_dummy_data():
    conn = sqlite3.connect("Homeapp.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # --- PERSON entries ---
    persons = [
        (1001, "Alice", "Smith", "alice", "pass123"),     # Client
        (1002, "Bob", "Johnson", "bob", "pass123"),       # Client
        (1003, "Cara", "Lee", "cara", "pass123"),         # Client
        (2001, "Dan", "Rogers", "dan", "pass123"),        # Homeowner
        (2002, "Eva", "Wells", "eva", "pass123"),         # Homeowner
        (3001, "Frank", "Moore", "frank", "pass123"),     # Employee
        (3002, "Grace", "Kim", "grace", "pass123"),       # Employee
    ]
    cursor.executemany("INSERT OR IGNORE INTO PERSON VALUES (?, ?, ?, ?, ?)", persons)

    # --- CLIENTS ---
    cursor.executemany("INSERT OR IGNORE INTO CLIENT (SSN) VALUES (?)", [(1001,), (1002,), (1003,)])

    # --- HOMEOWNERS ---
    cursor.executemany("INSERT OR IGNORE INTO HOMEOWNER (SSN) VALUES (?)", [(2001,), (2002,)])

    # --- EMPLOYEES ---
    cursor.executemany("INSERT OR IGNORE INTO EMPLOYEE (SSN, JobType) VALUES (?, ?)", [
        (3001, "Technician"),
        (3002, "Cleaner")
    ])

    # --- COMPANIES ---
    cursor.execute("INSERT OR IGNORE INTO COMPANY VALUES (?, ?, ?)", (1, "AllFixers Inc", "Maintenance"))

    # --- UPDATED WORKS_FOR ---
    cursor.executemany("INSERT OR IGNORE INTO WORKS_FOR (EmployeeSSN, CompanyID) VALUES (?, ?)", [
        (3001, 1),
        (3002, 1)
    ])

    # --- PROPERTIES ---
    properties = [
        (4001, "101 Elm Street", "Apartment block A", 2001),  # Apartment
        (4002, "202 Oak Street", "Apartment block B", 2001),  # Apartment
        (4003, "303 Pine Street", "Spacious house", 2002),    # House
    ]
    cursor.executemany("INSERT OR IGNORE INTO PROPERTY VALUES (?, ?, ?, ?)", properties)

    # --- APARTMENTS ---
    cursor.executemany("INSERT OR IGNORE INTO APARTMENT VALUES (?, ?)", [
        (4001, 1),
        (4002, 2)
    ])

    # --- HOUSE ---
    cursor.execute("INSERT OR IGNORE INTO HOUSE VALUES (?, ?)", (4003, 2))

    # --- LEASE AGREEMENTS ---
    leases = [
        (5001, "2024-01-01", "2025-01-01", 2001, 1001),  # Alice rents Apt 1
        (5002, "2024-02-01", "2025-02-01", 2001, 1002),  # Bob rents Apt 2
        (5003, "2024-03-01", "2025-03-01", 2002, 1003),  # Cara rents House
    ]
    cursor.executemany("INSERT OR IGNORE INTO LEASEAGREEMENT VALUES (?, ?, ?, ?, ?)", leases)

    # --- ROOMS ---
    # Apartment 1 (3 rooms)
    for room_number in range(1, 4):
        cursor.execute("INSERT OR IGNORE INTO ROOM VALUES (?, ?, ?, ?)", (4001, room_number, "Good", 5001))

    # Apartment 2 (3 rooms)
    for room_number in range(1, 4):
        cursor.execute("INSERT OR IGNORE INTO ROOM VALUES (?, ?, ?, ?)", (4002, room_number, "Good", 5002))

    # House (4 rooms)
    for room_number in range(1, 5):
        cursor.execute("INSERT OR IGNORE INTO ROOM VALUES (?, ?, ?, ?)", (4003, room_number, "Excellent", 5003))

    # --- RENTS ---
    cursor.execute("INSERT OR IGNORE INTO RENTS VALUES (?, ?, ?)", (4001, 1, 1001))
    cursor.execute("INSERT OR IGNORE INTO RENTS VALUES (?, ?, ?)", (4002, 1, 1002))
    cursor.execute("INSERT OR IGNORE INTO RENTS VALUES (?, ?, ?)", (4003, 1, 1003))

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    insert_dummy_data()
