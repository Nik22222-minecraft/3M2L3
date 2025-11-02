import sqlite3
from config import DATABASE

def clear_skills_status():
    conn = sqlite3.connect(DATABASE)
    with conn:
        conn.execute("DELETE FROM skills")
        conn.execute("DELETE FROM status")
        conn.commit()
    print(" Таблицы очищены.")

if __name__ == "__main__":
    clear_skills_status()
