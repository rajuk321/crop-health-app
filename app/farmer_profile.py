import sqlite3

def create_profile_table():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS profile(
                name TEXT,
                crop TEXT,
                soil TEXT,
                location TEXT)""")
    conn.commit()
    conn.close()

def save_profile(name,crop,soil,location):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("DELETE FROM profile")
    c.execute("INSERT INTO profile VALUES(?,?,?,?)",(name,crop,soil,location))
    conn.commit()
    conn.close()

def get_profile():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM profile")
    data=c.fetchone()
    conn.close()
    return data
