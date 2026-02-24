import sqlite3

class GetStudentData:

    def learning_goal_id(self, entry_id):
        con = sqlite3.connect("database.db")
        cur = con.cursor()

        cur.execute("""
        SELECT learning_goal_id
        FROM entry_learning_goals
        WHERE entry_id = ?
        """, (entry_id,))

        result = cur.fetchall()
        con.close()
        return result

    def collect_entries(self, student_id):
        con = sqlite3.connect("database.db")
        cur = con.cursor()

        cur.execute("""
        SELECT id, subject_id
        FROM entries
        WHERE student_id = ?
        """, (student_id,))

        entries = cur.fetchall()
        con.close()
        return entries




