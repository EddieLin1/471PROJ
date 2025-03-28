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
        FOREIGN KEY (ClientSSN) REFERENCES HOMEOWNER(SSN)
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
        OwnerSSN INTEGER,
        EmployeeSSN INTEGER,
        CompanyID INTEGER,
        PRIMARY KEY (OwnerSSN, EmployeeSSN, CompanyID),
        FOREIGN KEY (OwnerSSN) REFERENCES HOMEOWNER(SSN)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
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

if __name__ == "__main__":
    init_db()
