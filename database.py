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
        Password TEXT,
        Phone TEXT
    );

    CREATE TABLE IF NOT EXISTS CLIENT (
        SSN INTEGER PRIMARY KEY,
        FOREIGN KEY (SSN) REFERENCES PERSON(SSN)
        ON DELETE CASCADE ON UPDATE CASCADE
    );

    CREATE TABLE IF NOT EXISTS HOMEOWNER (
        SSN INTEGER PRIMARY KEY,
        FOREIGN KEY (SSN) REFERENCES PERSON(SSN)
        ON DELETE CASCADE ON UPDATE CASCADE
    );

    CREATE TABLE IF NOT EXISTS EMPLOYEE (
        SSN INTEGER PRIMARY KEY,
        JobType TEXT,
        FOREIGN KEY (SSN) REFERENCES PERSON(SSN)
        ON DELETE CASCADE ON UPDATE CASCADE
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
        ON DELETE CASCADE ON UPDATE CASCADE
    );

    CREATE TABLE IF NOT EXISTS APARTMENT (
        PropertyID INTEGER PRIMARY KEY,
        FloorNumber INTEGER,
        FOREIGN KEY (PropertyID) REFERENCES PROPERTY(PropertyID)
        ON DELETE CASCADE ON UPDATE CASCADE
    );

    CREATE TABLE IF NOT EXISTS HOUSE (
        PropertyID INTEGER PRIMARY KEY,
        NumFloors INTEGER,
        FOREIGN KEY (PropertyID) REFERENCES PROPERTY(PropertyID)
        ON DELETE CASCADE ON UPDATE CASCADE
    );

    CREATE TABLE IF NOT EXISTS ROOM (
        PropertyID INTEGER,
        RoomID INTEGER,
        Condition TEXT,
        PRIMARY KEY (PropertyID, RoomID),
        FOREIGN KEY (PropertyID) REFERENCES PROPERTY(PropertyID)
        ON DELETE CASCADE ON UPDATE CASCADE
    );

    CREATE TABLE IF NOT EXISTS LEASEAGREEMENT (
        LeaseID INTEGER PRIMARY KEY,
        StartDate TEXT,
        EndDate TEXT,
        PropertyID INTEGER,
        RoomID INTEGER,
        OwnerSSN INTEGER NOT NULL,
        ClientSSN INTEGER NOT NULL,
        FOREIGN KEY (PropertyID, RoomID) REFERENCES ROOM(PropertyID, RoomID)
        ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (OwnerSSN) REFERENCES HOMEOWNER(SSN)
        ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (ClientSSN) REFERENCES CLIENT(SSN)
        ON DELETE CASCADE ON UPDATE CASCADE
    );

    CREATE TABLE IF NOT EXISTS WORKS_FOR (
        EmployeeSSN INTEGER,
        CompanyID INTEGER,
        PRIMARY KEY (EmployeeSSN, CompanyID),
        FOREIGN KEY (EmployeeSSN) REFERENCES EMPLOYEE(SSN)
        ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (CompanyID) REFERENCES COMPANY(CompanyID)
        ON DELETE CASCADE ON UPDATE CASCADE
    );

    CREATE TABLE IF NOT EXISTS WORKS_ON (
        PropertyID INTEGER,
        RoomID INTEGER,
        ESSN INTEGER,
        PRIMARY KEY (PropertyID, RoomID, ESSN),
        FOREIGN KEY (PropertyID, RoomID) REFERENCES ROOM(PropertyID, RoomID)
        ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (ESSN) REFERENCES EMPLOYEE(SSN)
        ON DELETE CASCADE ON UPDATE CASCADE
    );

    CREATE TABLE IF NOT EXISTS REQUESTS (
        PropertyID INTEGER,
        RoomID INTEGER,
        ClientSSN INTEGER,
        PRIMARY KEY (PropertyID, RoomID, ClientSSN),
        FOREIGN KEY (PropertyID, RoomID) REFERENCES ROOM(PropertyID, RoomID)
        ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (ClientSSN) REFERENCES CLIENT(SSN)
        ON DELETE CASCADE ON UPDATE CASCADE
    );
    """)

    conn.commit()
    conn.close()

def insert_dummy_data():
    conn = sqlite3.connect("Homeapp.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # PERSON
    persons = [
        (1001, "Alice", "Smith", "alice", "pass123", "123-456-7890"),
        (1002, "Bob", "Johnson", "bob", "pass123", "234-567-8901"),
        (1003, "Cara", "Lee", "cara", "pass123", "345-678-9012"),
        (2001, "Dan", "Rogers", "dan", "pass123", "456-789-0123"),
        (2002, "Eva", "Wells", "eva", "pass123", "567-890-1234"),
        (3001, "Frank", "Moore", "frank", "pass123", "678-901-2345"),
        (3002, "Grace", "Kim", "grace", "pass123", "789-012-3456"),
        (3003, "Peter", "Janko", "peter", "pass123", "890-123-4567"),
    ]
    cursor.executemany("INSERT OR IGNORE INTO PERSON VALUES (?, ?, ?, ?, ?, ?)", persons)

    # CLIENT, HOMEOWNER, EMPLOYEE
    cursor.executemany("INSERT OR IGNORE INTO CLIENT VALUES (?)", [(1001,), (1002,), (1003,)])
    cursor.executemany("INSERT OR IGNORE INTO HOMEOWNER VALUES (?)", [(2001,), (2002,)])
    cursor.executemany("INSERT OR IGNORE INTO EMPLOYEE VALUES (?, ?)", [
        (3001, "Technician"), (3002, "Cleaner"), (3003, "Plumber")
    ])

    # COMPANIES, WORKS_FOR
    cursor.executemany("INSERT OR IGNORE INTO COMPANY VALUES (?, ?, ?)", [
        (1, "AllFixers Inc", "Maintenance"),
        (2, "BigFixCompany Inc", "Maintenance")
    ])
    cursor.executemany("INSERT OR IGNORE INTO WORKS_FOR VALUES (?, ?)", [
        (3001, 1), (3002, 1), (3003, 2)
    ])

    # PROPERTIES
    properties = [
        (4001, "101 Elm Street", "Apartment block A", 2001),
        (4002, "202 Oak Street", "Apartment block B", 2001),
        (5001, "303 Pine Street", "Spacious house", 2002)
    ]
    cursor.executemany("INSERT OR IGNORE INTO PROPERTY VALUES (?, ?, ?, ?)", properties)

    # APARTMENTS & HOUSE
    cursor.executemany("INSERT OR IGNORE INTO APARTMENT VALUES (?, ?)", [(4001, 1), (4002, 2)])
    cursor.execute("INSERT OR IGNORE INTO HOUSE VALUES (?, ?)", (5001, 2))

    # ROOMS
    for room in range(1, 4):  # Apt 1
        cursor.execute("INSERT OR IGNORE INTO ROOM VALUES (?, ?, ?)", (4001, room, "Good"))
    for room in range(1, 4):  # Apt 2
        cursor.execute("INSERT OR IGNORE INTO ROOM VALUES (?, ?, ?)", (4002, room, "Good"))
    for room in range(1, 5):  # House
        cursor.execute("INSERT OR IGNORE INTO ROOM VALUES (?, ?, ?)", (5001, room, "Excellent"))

    # ✅ Commit before using rooms in FK constraints
    conn.commit()

    # LEASE AGREEMENTS
    leases = [
        (6001, "2024-01-01", "2025-01-01", 4001, 1, 2001, 1001),
        (6002, "2024-02-01", "2025-02-01", 4001, 2, 2001, 1002),
        (6003, "2024-03-01", "2025-03-01", 5001, 1, 2002, 1003),
    ]
    cursor.executemany("INSERT OR IGNORE INTO LEASEAGREEMENT VALUES (?, ?, ?, ?, ?, ?, ?)", leases)

    # REQUESTS
    cursor.execute("INSERT OR IGNORE INTO REQUESTS VALUES (?, ?, ?)", (4001, 1, 1001))
    cursor.execute("INSERT OR IGNORE INTO REQUESTS VALUES (?, ?, ?)", (4002, 1, 1002))
    cursor.execute("INSERT OR IGNORE INTO REQUESTS VALUES (?, ?, ?)", (5001, 1, 1003))
    # WORKS_ON
    cursor.execute("INSERT OR IGNORE INTO WORKS_ON VALUES (?, ?, ?)", (4001, 1, 3001))
    

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    insert_dummy_data()
