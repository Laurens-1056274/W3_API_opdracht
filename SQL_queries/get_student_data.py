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
            SELECT DISTINCT lg.id, lg.title
            FROM learning_goals lg
            JOIN entry_learning_goals elg ON lg.id = elg.learning_goal_id
            JOIN entries e ON elg.entry_id = e.id
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
