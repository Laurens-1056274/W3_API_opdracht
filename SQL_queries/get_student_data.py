import sqlite3

class GetStudentData:

    def get_learning_goal_overview(self, student_id):
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()

        # 1) Taxonomy averages per learning_goal_id + level,
        #    gebaseerd op snapshots die gekoppeld zijn aan learning_goals
        #    die via entries van deze student voorkomen.
        cursor.execute("""
            WITH student_learning_goals AS (
                SELECT DISTINCT elg.learning_goal_id
                FROM entries e
                JOIN entry_learning_goals elg ON elg.entry_id = e.id
                WHERE e.student_id = ?
            ),
            student_snapshots AS (
                SELECT DISTINCT s.id AS snapshot_id, s.learning_goal_id
                FROM snapshots s
                JOIN student_learning_goals slg ON slg.learning_goal_id = s.learning_goal_id
            )
            SELECT
                lg.id AS learning_goal_id,
                lg.title AS learning_goal_title,
                st.level AS taxonomy_level,
                AVG(st.kennen) AS avg_kennen,
                AVG(st.kunnen) AS avg_kunnen,
                AVG(st.confidence) AS avg_confidence
            FROM student_snapshots ss
            JOIN learning_goals lg ON lg.id = ss.learning_goal_id
            JOIN snapshot_taxonomy st ON st.snapshot_id = ss.snapshot_id
            GROUP BY
                lg.id,
                lg.title,
                st.level
            ORDER BY
                lg.id,
                st.level
        """, (student_id,))

        taxonomy_rows = cursor.fetchall()

        # 2) Keywords alleen voor learning goals die bij deze student horen
        cursor.execute("""
            SELECT DISTINCT
                lg.id AS learning_goal_id,
                lgk.keyword AS keyword
            FROM entries e
            JOIN entry_learning_goals elg ON elg.entry_id = e.id
            JOIN learning_goals lg ON lg.id = elg.learning_goal_id
            JOIN learning_goal_keywords lgk ON lgk.learning_goal_id = lg.id
            WHERE e.student_id = ?
            ORDER BY lg.id
        """, (student_id,))

        keyword_rows = cursor.fetchall()

        connection.close()

        # 3) Bouw datastructuur
        learning_goals = {}

        for row in taxonomy_rows:
            learning_goal_id = row[0]
            title = row[1]
            level = row[2]
            avg_kennen = row[3]
            avg_kunnen = row[4]
            avg_confidence = row[5]

            if learning_goal_id not in learning_goals:
                learning_goals[learning_goal_id] = {
                    "title": title,
                    "keywords": [],
                    "taxonomy": {}
                }

            learning_goals[learning_goal_id]["taxonomy"][level] = {
                "kennen": round(avg_kennen, 2) if avg_kennen is not None else None,
                "kunnen": round(avg_kunnen, 2) if avg_kunnen is not None else None,
                "confidence": round(avg_confidence, 2) if avg_confidence is not None else None
            }

        for row in keyword_rows:
            learning_goal_id = row[0]
            keyword = row[1]

            # alleen toevoegen als het learning_goal_id al bestaat (dus echt bij student hoort)
            if learning_goal_id in learning_goals:
                learning_goals[learning_goal_id]["keywords"].append(keyword)

        return learning_goals