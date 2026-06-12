import sqlite3
from typing import Any


class GetClassData:
    """Retrieves class-related data from the SQLite database."""

    DB_PATH = "database.db"

    def __init__(self):
        self.con = sqlite3.connect(self.DB_PATH)
        self.con.row_factory = sqlite3.Row
        self.con.execute("PRAGMA foreign_keys = ON;")

    def close(self):
        self.con.close()

    def get_classes(self) -> list[str]:
        """Return all class names from students table, sorted alphabetically."""
        cur = self.con.execute(
            """
            SELECT DISTINCT klas
            FROM students
            WHERE klas IS NOT NULL AND TRIM(klas) <> ''
            ORDER BY klas
            """
        )
        return [row["klas"] for row in cur.fetchall()]

    def get_learning_goal_overview_for_class(self, klas: str) -> list[dict[str, Any]]:
        """Return all learning goals for a class with snapshots and averages."""
        learning_goals = self._get_learning_goals_for_class(klas)
        result: list[dict[str, Any]] = []

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

    def get_students_overview_for_class(self, klas: str) -> list[dict[str, Any]]:
        """Return students in a class with global kennen/kunnen progress and status."""
        cur = self.con.execute(
            """
            SELECT
                st.id,
                st.name,
                AVG(stx.kennen) AS avg_kennen,
                AVG(stx.kunnen) AS avg_kunnen
            FROM students st
            LEFT JOIN entries e ON e.student_id = st.id
            LEFT JOIN entry_learning_goals elg ON elg.entry_id = e.id
            LEFT JOIN snapshots s ON s.learning_goal_id = elg.learning_goal_id
            LEFT JOIN snapshot_taxonomy stx ON stx.snapshot_id = s.id
            WHERE st.klas = ?
            GROUP BY st.id, st.name
            ORDER BY st.name
            """,
            (klas,),
        )

        result: list[dict[str, Any]] = []
        for row in cur.fetchall():
            avg_kennen = row["avg_kennen"]
            avg_kunnen = row["avg_kunnen"]

            kennen_pct = round(
                avg_kennen * 100, 1) if avg_kennen is not None else None
            kunnen_pct = round(
                avg_kunnen * 100, 1) if avg_kunnen is not None else None

            if kennen_pct is None or kunnen_pct is None:
                status = "Geen data"
                global_progress = None
            else:
                global_progress = round((kennen_pct + kunnen_pct) / 2, 1)
                status = self._status_for_progress(global_progress)

            result.append(
                {
                    "id": row["id"],
                    "name": row["name"],
                    "avg_kennen": kennen_pct,
                    "avg_kunnen": kunnen_pct,
                    "global_progress": global_progress,
                    "status": status,
                }
            )

        return result

    def _get_learning_goals_for_class(self, klas: str) -> list[sqlite3.Row]:
        cur = self.con.execute(
            """
            SELECT DISTINCT
                lg.id,
                lg.title,
                sub.name AS subject
            FROM students st
            JOIN entries e ON e.student_id = st.id
            JOIN subjects sub ON sub.id = e.subject_id
            JOIN entry_learning_goals elg ON elg.entry_id = e.id
            JOIN learning_goals lg ON lg.id = elg.learning_goal_id
            WHERE st.klas = ?
            ORDER BY lg.title
            """,
            (klas,),
        )
        return cur.fetchall()

    def _get_keywords(self, learning_goal_id: str) -> list[str]:
        cur = self.con.execute(
            "SELECT keyword FROM learning_goal_keywords WHERE learning_goal_id = ?",
            (learning_goal_id,),
        )
        return [row["keyword"] for row in cur.fetchall()]

    def _get_snapshots(self, learning_goal_id: str) -> list[dict[str, Any]]:
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

        snapshots: list[dict[str, Any]] = []
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

    def _get_snapshot_taxonomy(self, snapshot_id: int) -> list[dict[str, Any]]:
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
    def _calc_averages(snapshots: list[dict[str, Any]]) -> tuple[float | None, float | None]:
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

        avg_kennen = round(sum(kennen_vals) / len(kennen_vals),
                           3) if kennen_vals else None
        avg_kunnen = round(sum(kunnen_vals) / len(kunnen_vals),
                           3) if kunnen_vals else None
        return avg_kennen, avg_kunnen

    @staticmethod
    def _status_for_progress(progress: float) -> str:
        if progress >= 75:
            return "Uitblinker"
        if progress < 55:
            return "Achterloopt"
        return "Op schema"
