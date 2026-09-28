import sqlite3

#datbase conenction for the bot
CPA_db = sqlite3.connect("cpa_tutor.db")

#creating Server table (We want our dataStored to be differentPerServer)
CPA_db.executescript("""
    CREATE TABLE IF NOT EXISTS Servers (
        serverID INTEGER PRIMARY KEY,
        serverName TEXT NOT NULL,
        memberCount INTEGER
    );

    CREATE TABLE IF NOT EXISTS Sections (
        sectionID INTEGER PRIMARY KEY,
        serverID INTEGER NOT NULL,
        sectionName TEXT NOT NULL,

        FOREIGN KEY (ServerID) REFERENCES Servers(ServerID),
        UNIQUE (ServerID, SectionName)
    );

    CREATE TABLE IF NOT EXISTS Tasks (
        taskID INT PRIMARY KEY,
        sectionID INTEGER NOT NULL,
        taskName TEXT NOT NULL,
        addedBy INTEGER NOT NULL,
        courseName TEXT NOT NULL,
        dueDate INTEGER NOT NULL,

        FOREIGN KEY (SectionID) REFERENCES Sections(SectionID)
    );
""")

def add_server(server_id:int, server_name:str, memberCount:int):
    CPA_db.execute("""
        INSERT INTO Servers (serverID, serverName, memberCount)
        VALUES (?, ?, ?)
        ON CONFLICT(serverID) DO UPDATE SET
            serverName = excluded.serverName,
            memberCount = excluded.memberCOunt
    """, (server_id, server_name, memberCount))

    CPA_db.commit()

def add_section(server_id:int, section_name:str):
    CPA_db.execute("""
        INSERT OR IGNORE INTO Sections (serverID, sectionName)
        VALUES (?, ?)
    """, (server_id, section_name))

    CPA_db.commit()

def display_section(server_id:int):
    rows = CPA_db.execute("""
        SELECT sectionName
        FROM Sections
        WHERE serverID = ?
        ORDER BY sectionName
    """, (server_id,)).fetchall()

    return rows

def add_task(task_id:int, section_id:int, task_name:str, addedBy:int, course_name:str, due_date:int):
    pass

def display_tasks(server_id:int, section_id:int):
    pass