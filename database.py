import sqlite3

#datbase conenction for the bot
CPA_db = sqlite3.connect("cpa_tutor.db")

#creating Server table (We want our dataStored to be differentPerServer)
CPA_db.executescript("""
    CREATE TABLE IF NOT EXISTS Servers (
        serverID INTEGER PRIMARY KEY,
        serverName TEXT NOT NULL,
        memberCount INTEGER,

        restrictedDeleteSection INTEGER NOT NULL DEFAULT 1
            CHECK (restrictedDeleteSection IN (0, 1)),

        restrictedDeleteTask INTEGER NOT NULL DEFAULT 0
            CHECK (restrictedDeleteTask IN (0, 1)),

        restrictedAddTask INTEGER NOT NULL DEFAULT 0
            CHECK (restrictedAddTask IN (0, 1)),

        restrictedAddSection INTEGER NOT NULL DEFAULT 1
            CHECK (restrictedAddSection IN (0, 1)),

        morningChannel INTEGER,
        questionChannel INTEGER,
        updateChannel INTEGER,
        restrictionBypass INTEGER,

        lastQuestionDate TEXT,
        lastMorningDate TEXT
    );

    CREATE TABLE IF NOT EXISTS Sections (
        sectionID INTEGER PRIMARY KEY,
        serverID INTEGER NOT NULL,
        sectionName TEXT NOT NULL,

        FOREIGN KEY (ServerID) REFERENCES Servers(ServerID),
        UNIQUE (ServerID, SectionName)
    );

    CREATE TABLE IF NOT EXISTS Tasks (
        taskID INTEGER,
        sectionID INTEGER NOT NULL,
        taskName TEXT NOT NULL,
        addedBy INTEGER NOT NULL,
        courseName TEXT NOT NULL,
        dueDate INTEGER NOT NULL,

        PRIMARY KEY (taskID, sectionID)
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

def get_sectionID(section_name:str, server_id:int):   
    section_id = CPA_db.execute("""
        SELECT sectionID
        FROM Sections
        WHERE Sections.sectionName = ? AND Sections.serverID = ?
    """, (section_name, server_id)).fetchone()

    return section_id

def clear_tasks(section_name:str, server_id):
    section_id = get_sectionID(section_name, server_id)

    if section_id is None:
        return f'The section {section_name} does not exist!'

    CPA_db.execute("""
        DELETE FROM Tasks
        WHERE sectionID = ?
    """, (section_id[0],))

    CPA_db.commit()

    return f'Section: {section_name} is cleared!'

def remove_section(section_name:str, server_id:int):
    section_id = get_sectionID(section_name, server_id)

    if section_id is None:
        return f'The section {section_name} does not exist!'

    # Remove all related tasks first
    clear_tasks(server_id, section_name)

    # Remove section table
    CPA_db.execute("""
        DELETE FROM Sections
        WHERE sectionID = ? AND serverID = ?
    """, (section_id[0],server_id))

    CPA_db.commit()

    return f'Section: {section_name} has been removed!'

def add_task(section_name:str, server_id:int, task_name:str, addedBy:int, course_name:str, due_date:int):
    #Convert section_name to sectionID
    section_id = get_sectionID(section_name, server_id)

    if section_id is None:
        return f'The section {section_name} does not exist!'

    #Grab taskID
    rows = CPA_db.execute("""
        SELECT taskID
        FROM Tasks
        WHERE sectionID = ?
    """, (section_id[0],)).fetchall()

    used_ids = {row[0] for row in rows}

    taskID = None

    for number in range(1, 21):
        if number not in used_ids:
            taskID = number
            break

    if taskID is None:
        return f'The section: {section_name} has reached task limits'

    CPA_db.execute("""
        INSERT INTO Tasks (taskID, sectionID, taskName, addedBy, courseName, dueDate)
        VALUES (?,?,?,?,?,?)
    """, (taskID, section_id[0], task_name, addedBy, course_name, due_date))

    CPA_db.commit()

    return f'Sucessfully added "{task_name}" to section: {section_name}'

def remove_task(task_id:int, section_name:str, server_id:int):
    section_id = get_sectionID(section_name, server_id)

    if section_id is None:
        return f'The section {section_name} does not exist!'

    rows = CPA_db.execute("""
        DELETE FROM TASKS
        WHERE sectionID = ? AND taskID = ?
    """, (section_id[0], task_id))

    CPA_db.commit()

    print(rows.rowcount)
    if rows.rowcount == 0:
        return f'TaskID: {task_id} is not valid!'

    return f'Item has been removed'
    

def display_tasks(section_name:str, server_id:int):
    section_id = get_sectionID(section_name, server_id)

    if section_id is None:
        return -1

    rows = CPA_db.execute("""
        SELECT taskID, taskName, courseName, addedBy, dueDate
        FROM Tasks
        WHERE sectionID = ?
        ORDER BY dueDate
    """, (section_id[0],)).fetchall()

    if len(rows)==0:
        return 0

    return rows

def set_bypass(server_id:int, role_id:int):
    CPA_db.execute("""
        UPDATE Servers
        SET restrictionBypass = ?
        WHERE serverID = ?
    """, (role_id, server_id))

    CPA_db.commit()

def get_settings(server_id:int):
    allSettings = CPA_db.execute("""
        SELECT * FROM Servers
        WHERE serverID = ?
    """, (server_id,))

    columnNames = [column[0] for column in allSettings.description]

    return dict(zip(columnNames,allSettings.fetchone()))

def checkBypass(server_id:int):
    return CPA_db.execute("""
        SELECT restrictionBypass 
        FROM Servers
        WHERE serverID = ?
    """, (server_id,)).fetchone()[0]

def set_restriction(server_id:int, restrictionType:str, status:bool):
    allRestrictions = {"restrictedDeleteSection", "restrictedDeleteTask", "restrictedAddSection", "restrictedAddTask"}

    if restrictionType not in allRestrictions:
        return "restrictionType is not correct (Case Sensitive)"
    
    CPA_db.execute(f"""
        UPDATE Servers
        SET {restrictionType} = ?
        WHERE serverID = ?
    """, (int(status), server_id))

    CPA_db.commit()

    return f'{restrictionType} has been set to {status}'

def set_channel(server_id:int, channelType:str, location:int):
    allChannelType = {"morningChannel", "questionChannel", "updateChannel"}

    if channelType not in allChannelType:
            return "channelType is not correct (Case Sensitive)"

    CPA_db.execute(f"""
        UPDATE Servers
        SET {channelType} = ?
        WHERE serverID = ?
    """, (location, server_id))

    CPA_db.commit()

    return f'{channelType} has been relocated!'