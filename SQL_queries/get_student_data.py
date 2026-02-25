import sqlite3

class GetStudentData:

    def snapshot_taxonomy(self, snapshot_id):
        con = sqlite3.connect("database.db")
        cur = con.cursor()

        cur.execute("""
        SELECT level,kennen,kunnen,confidence
        FROM snapshot_taxonomy
        WHERE snapshot_id = ?
        """, (snapshot_id,))

        result = cur.fetchall()
        con.close()
        return result


    def snapshot_id(self, learning_goal_id):
        con = sqlite3.connect("database.db")
        cur = con.cursor()

        cur.execute("""
        SELECT id
        FROM snapshots
        WHERE learning_goal_id = ?
        """, (learning_goal_id,))

        result = cur.fetchall()
        con.close()
        return result


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
    
    def learning_goal_title(self, learning_goal_id):
        con = sqlite3.connect("database.db")
        cur = con.cursor()

        cur.execute("""
        SELECT title
        FROM learning_goals
        WHERE id = ?
        """, (learning_goal_id,))

        result = cur.fetchall()
        con.close()
        return result

    def collect_entries(self, student_id):
        con = sqlite3.connect("database.db")
        cur = con.cursor()

        cur.execute("""
        SELECT id
        FROM entries
        WHERE student_id = ?
        """, (student_id,))

        result = cur.fetchall()
        con.close()
        return result




