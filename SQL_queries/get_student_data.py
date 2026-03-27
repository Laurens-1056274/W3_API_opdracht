import sqlite3


class GetStudentData:
    """Retrieves student-related data from the SQLite database."""

    DB_PATH = "database.db"

    def __init__(self):
        self.con = sqlite3.connect(self.DB_PATH)
        self.con.row_factory = sqlite3.Row
        self.con.execute("PRAGMA foreign_keys = ON;")

    def close(self):
        self.con.close()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_learning_goal_overview(self, student_id: int) -> list[dict]:
        """Return all learning goals for *student_id* with keywords,
        snapshots and per-goal average kennen/kunnen scores.

        Returns a list of dicts:
        [
          {
            "id": str,
            "title": str,
            "keywords": [str, ...],
            "avg_kennen": float | None,
            "avg_kunnen": float | None,
            "snapshots": [
              {
                "at": str,
                "source": {"type": str, "id": str},
                "taxonomy": [
                  {"level": str, "kennen": float, "kunnen": float, "confidence": float},
                  ...
                ]
              },
              ...
            ]
          },
          ...
        ]
        """
        learning_goals = self._get_learning_goals_for_student(student_id)
        result = []
        for lg in learning_goals:
            lg_id = lg["id"]
            keywords = self._get_keywords(lg_id)
            snapshots = self._get_snapshots(lg_id)
            avg_kennen, avg_kunnen = self._calc_averages(snapshots)
            result.append(
                {
                    "id": lg_id,
                    "title": lg["title"],
                    "subject": lg["subject"],
                    "keywords": keywords,
                    "avg_kennen": avg_kennen,
                    "avg_kunnen": avg_kunnen,
                    "snapshots": snapshots,
                }
            )
        return result

    def get_student_info(self, student_id: int) -> dict | None:
        """Return basic student info (id, name) or None if not found."""
        cur = self.con.execute(
            "SELECT id, name FROM students WHERE id = ?", (student_id,)
        )
        row = cur.fetchone()
        return dict(row) if row else None

    def get_subjects_for_student(self, student_id: int) -> list[dict]:
        """Return all subjects a student has entries for."""
        cur = self.con.execute(
            """
            SELECT DISTINCT sub.id, sub.name
            FROM subjects sub
            JOIN entries e ON sub.id = e.subject_id
            WHERE e.student_id = ?
            ORDER BY sub.name
            """,
            (student_id,),
        )
        return [dict(row) for row in cur.fetchall()]

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_learning_goals_for_student(self, student_id: int) -> list[sqlite3.Row]:
        cur = self.con.execute(
            """
            SELECT DISTINCT 
                lg.id, 
                lg.title,
                sub.name AS subject
            FROM learning_goals lg
            JOIN entry_learning_goals elg ON lg.id = elg.learning_goal_id
            JOIN entries e ON elg.entry_id = e.id
            JOIN subjects sub ON e.subject_id = sub.id
            WHERE e.student_id = ?
            ORDER BY lg.title
            """,
            (student_id,),
        )
        return cur.fetchall()

    def _get_keywords(self, learning_goal_id: str) -> list[str]:
        cur = self.con.execute(
            "SELECT keyword FROM learning_goal_keywords WHERE learning_goal_id = ?",
            (learning_goal_id,),
        )
        return [row["keyword"] for row in cur.fetchall()]

    def _get_snapshots(self, learning_goal_id: str) -> list[dict]:
        cur = self.con.execute(
            """
            SELECT s.id AS snapshot_id, s.at, src.type AS source_type, src.external_id
            FROM snapshots s
            LEFT JOIN sources src ON s.source_id = src.id
            WHERE s.learning_goal_id = ?
            ORDER BY s.at
            """,
            (learning_goal_id,),
        )
        snapshots = []
        for row in cur.fetchall():
            taxonomy = self._get_snapshot_taxonomy(row["snapshot_id"])
            snapshots.append(
                {
                    "at": row["at"],
                    "source": {
                        "type": row["source_type"],
                        "id": row["external_id"],
                    },
                    "taxonomy": taxonomy,
                }
            )
        return snapshots

    def _get_snapshot_taxonomy(self, snapshot_id: int) -> list[dict]:
        cur = self.con.execute(
            """
            SELECT level, kennen, kunnen, confidence
            FROM snapshot_taxonomy
            WHERE snapshot_id = ?
            ORDER BY rowid
            """,
            (snapshot_id,),
        )
        return [dict(row) for row in cur.fetchall()]
    
    def profiel(self, user_type, student_name: str, student_id: int):
            if user_type == "leerling":
                cur = self.con.execute(
                """
                SELECT *
                FROM students
                WHERE name = ? AND  id = ?
                """,
                (student_name,student_id),
                )
            if user_type == "docent":
                cur = self.con.execute(
                """
                SELECT *
                FROM teachers
                WHERE name = ? AND  id = ?
                """,
                (student_name,student_id),
                )

            return [dict(row) for row in cur.fetchall()]


    @staticmethod
    def _calc_averages(snapshots: list[dict]) -> tuple[float | None, float | None]:
        """Calculate overall average kennen and kunnen across all snapshots."""
        kennen_vals = [
            t["kennen"]
            for s in snapshots
            for t in s["taxonomy"]
            if t["kennen"] is not None
        ]
        kunnen_vals = [
            t["kunnen"]
            for s in snapshots
            for t in s["taxonomy"]
            if t["kunnen"] is not None
        ]
        avg_kennen = round(sum(kennen_vals) / len(kennen_vals), 3) if kennen_vals else None
        avg_kunnen = round(sum(kunnen_vals) / len(kunnen_vals), 3) if kunnen_vals else None
        return avg_kennen, avg_kunnen
    def get_class_analysis(self, class_name: str) -> dict:
        """Return class analysis data for the given class."""
        # Get all students in the class
        cur = self.con.execute(
            "SELECT id, name FROM students WHERE klas = ?",
            (class_name,)
        )
        students = cur.fetchall()
        
        if not students:
            return {"learning_goals": [], "taxonomy_analysis": {}, "problematic_keywords": []}
        
        # Collect all learning goals data for the class
        all_learning_goals = {}
        taxonomy_data = {}
        keyword_data = {}
        
        for student in students:
            student_id = student["id"]
            goals = self.get_learning_goal_overview(student_id)
            
            for goal in goals:
                goal_id = goal["id"]
                if goal_id not in all_learning_goals:
                    all_learning_goals[goal_id] = {
                        "id": goal_id,
                        "title": goal["title"],
                        "keywords": goal["keywords"],
                        "students": []
                    }
                
                # Add this student's scores
                all_learning_goals[goal_id]["students"].append({
                    "kennen": goal["avg_kennen"],
                    "kunnen": goal["avg_kunnen"]
                })
                
                # Collect taxonomy data
                for snapshot in goal["snapshots"]:
                    for tax in snapshot["taxonomy"]:
                        level = tax["level"]
                        if level not in taxonomy_data:
                            taxonomy_data[level] = []
                        taxonomy_data[level].append({
                            "kennen": tax["kennen"],
                            "kunnen": tax["kunnen"]
                        })
                
                # Collect keyword data
                for keyword in goal["keywords"]:
                    if keyword not in keyword_data:
                        keyword_data[keyword] = []
                    keyword_data[keyword].append({
                        "kennen": goal["avg_kennen"],
                        "kunnen": goal["avg_kunnen"]
                    })
        
        # Calculate averages for learning goals
        learning_goals_result = []
        for goal_id, goal_data in all_learning_goals.items():
            students_data = goal_data["students"]
            valid_kennen = [s["kennen"] for s in students_data if s["kennen"] is not None]
            valid_kunnen = [s["kunnen"] for s in students_data if s["kunnen"] is not None]
            
            avg_kennen = sum(valid_kennen) / len(valid_kennen) if valid_kennen else 0
            avg_kunnen = sum(valid_kunnen) / len(valid_kunnen) if valid_kunnen else 0
            
            # Determine strength
            avg_overall = (avg_kennen + avg_kunnen) / 2
            if avg_overall >= 0.7:
                strength = "strong"
            elif avg_overall >= 0.4:
                strength = "neutral"
            else:
                strength = "weak"
            
            learning_goals_result.append({
                "id": goal_data["id"],
                "title": goal_data["title"],
                "keywords": goal_data["keywords"],
                "avg_kennen": avg_kennen,
                "avg_kunnen": avg_kunnen,
                "strength": strength
            })
        
        # Calculate taxonomy averages
        taxonomy_result = {}
        for level, data in taxonomy_data.items():
            valid_kennen = [d["kennen"] for d in data if d["kennen"] is not None]
            valid_kunnen = [d["kunnen"] for d in data if d["kunnen"] is not None]
            
            taxonomy_result[level] = {
                "avg_kennen": sum(valid_kennen) / len(valid_kennen) if valid_kennen else 0,
                "avg_kunnen": sum(valid_kunnen) / len(valid_kunnen) if valid_kunnen else 0,
                "count": len(data)
            }
        
        # Find problematic keywords (lowest average scores)
        keywords_result = []
        for keyword, data in keyword_data.items():
            valid_kennen = [d["kennen"] for d in data if d["kennen"] is not None]
            valid_kunnen = [d["kunnen"] for d in data if d["kunnen"] is not None]
            
            if valid_kennen and valid_kunnen:
                avg_kennen = sum(valid_kennen) / len(valid_kennen)
                avg_kunnen = sum(valid_kunnen) / len(valid_kunnen)
                avg_overall = (avg_kennen + avg_kunnen) / 2
                
                keywords_result.append({
                    "keyword": keyword,
                    "avg_kennen": avg_kennen,
                    "avg_kunnen": avg_kunnen,
                    "avg": avg_overall
                })
        
        # Sort keywords by lowest average (most problematic first)
        keywords_result.sort(key=lambda x: x["avg"])
        keywords_result = keywords_result[:10]  # Top 10 most problematic
        
        return {
            "learning_goals": learning_goals_result,
            "taxonomy_analysis": taxonomy_result,
            "problematic_keywords": keywords_result
        }

    def get_class_analysis(self):
        # Leerdoelen
        cur = self.con.execute("""
            SELECT lg.title, AVG(st.kennen) as kennen, AVG(st.kunnen) as kunnen
            FROM learning_goals lg
            JOIN snapshots s ON lg.id = s.learning_goal_id
            JOIN snapshot_taxonomy st ON s.id = st.snapshot_id
            GROUP BY lg.id, lg.title
            ORDER BY (AVG(st.kennen) + AVG(st.kunnen)) / 2 DESC
        """)
        goals = cur.fetchall()
        
        # Taxonomieniveaus
        cur = self.con.execute("""
            SELECT st.level, AVG(st.kennen) as kennen, AVG(st.kunnen) as kunnen
            FROM snapshot_taxonomy st
            GROUP BY st.level
            ORDER BY (AVG(st.kennen) + AVG(st.kunnen)) / 2 ASC
        """)
        taxonomy = cur.fetchall()
        
        # Kernwoorden
        cur = self.con.execute("""
            SELECT lkw.keyword, AVG(st.kennen) as kennen, AVG(st.kunnen) as kunnen
            FROM learning_goal_keywords lkw
            JOIN snapshots s ON lkw.learning_goal_id = s.learning_goal_id
            JOIN snapshot_taxonomy st ON s.id = st.snapshot_id
            GROUP BY lkw.keyword
            ORDER BY (AVG(st.kennen) + AVG(st.kunnen)) / 2 ASC
            LIMIT 10
        """)
        keywords = cur.fetchall()
        
        return {
            'goals': goals,
            'taxonomy': taxonomy,
            'keywords': keywords
        }