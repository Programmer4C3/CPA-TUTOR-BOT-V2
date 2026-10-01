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

def add_task(section_name:str, server_id:int, task_name:str, addedBy:int, course_name:str, due_date:int):
    section_id = CPA_db.execute("""
        SELECT sectionID
        FROM Sections
        WHERE Sections.sectionName = ? AND Sections.serverID = ?
    """, (section_name, server_id)).fetchone()

    if section_id is None:
        return None

    CPA_db.execute("""
        INSERT OR IGNORE INTO Tasks (sectionID, taskName, addedBy, courseName, dueDate)
        VALUES (?,?,?,?,?)
    """, (section_id[0], task_name, addedBy, course_name, due_date))

    CPA_db.commit()

    return True

def display_tasks(section_name:str, server_id:int):
    section_id = CPA_db.execute("""
        SELECT sectionID
        FROM Sections
        WHERE Sections.sectionName = ? AND Sections.serverID = ?
    """, (section_name, server_id)).fetchone()

    if section_id is None:
        return -1

    rows = CPA_db.execute("""
        SELECT taskName, addedBy, courseName, dueDate
        FROM Tasks
        WHERE sectionID = ?
        ORDER BY dueDate
    """, (section_id[0],)).fetchall()

    if len(rows)==0:
        return 0

    return rows