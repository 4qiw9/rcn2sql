import sqlite3
import os
from datetime import datetime


def ensure_import_meta_schema(conn: sqlite3.Connection) -> None:
    """Create import metadata table."""
    conn.execute("""
    CREATE TABLE IF NOT EXISTS _import_meta (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_file TEXT NOT NULL,
        file_size INTEGER,
        status TEXT NOT NULL DEFAULT 'pending',
        started_at TEXT,
        completed_at TEXT,
        records_inserted INTEGER,
        duration_seconds REAL
    );
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_import_source ON _import_meta(source_file);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_import_status ON _import_meta(status);")


def is_file_imported(conn: sqlite3.Connection, source_file: str) -> dict | None:
    """
    Check if file was already successfully imported (exact match by name).

    Returns:
        None if not imported, or dict with import info if found.
    """
    filename = os.path.basename(source_file)

    cursor = conn.execute(
        "SELECT id, file_size, records_inserted FROM _import_meta WHERE source_file = ? AND status = 'completed' ORDER BY id DESC LIMIT 1",
        (filename,)
    )
    row = cursor.fetchone()

    if not row:
        return None

    import_id, stored_size, records = row
    return {"id": import_id, "file_size": stored_size, "records_inserted": records}


def find_suspected_duplicate(conn: sqlite3.Connection, source_file: str) -> dict | None:
    """
    Check if there's a completed import with same file size (different name).

    Returns:
        None if no suspected duplicate, or dict with import info if found.
    """
    filename = os.path.basename(source_file)
    file_size = os.path.getsize(source_file) if os.path.exists(source_file) else None

    if not file_size:
        return None

    cursor = conn.execute(
        """SELECT id, source_file, file_size, records_inserted 
           FROM _import_meta 
           WHERE file_size = ? AND source_file != ? AND status = 'completed' 
           ORDER BY id DESC LIMIT 1""",
        (file_size, filename)
    )
    row = cursor.fetchone()

    if not row:
        return None

    import_id, other_filename, stored_size, records = row
    return {
        "id": import_id,
        "source_file": other_filename,
        "file_size": stored_size,
        "records_inserted": records
    }


def start_import(conn: sqlite3.Connection, source_file: str) -> int:
    """Start an import and return the import_id."""
    file_size = os.path.getsize(source_file) if os.path.exists(source_file) else None
    cursor = conn.execute(
        "INSERT INTO _import_meta (source_file, file_size, status, started_at) VALUES (?, ?, 'pending', ?)",
        (os.path.basename(source_file), file_size, datetime.now().isoformat())
    )
    conn.commit()
    return cursor.lastrowid


def complete_import(conn: sqlite3.Connection, import_id: int, records: int, duration: float) -> None:
    """Mark import as completed."""
    conn.execute(
        """UPDATE _import_meta 
           SET status = 'completed', 
               completed_at = ?, 
               records_inserted = ?, 
               duration_seconds = ?
           WHERE id = ?""",
        (datetime.now().isoformat(), records, duration, import_id)
    )
    conn.commit()


def fail_import(conn: sqlite3.Connection, import_id: int, error: str = None) -> None:
    """Mark import as failed."""
    conn.execute(
        """UPDATE _import_meta 
           SET status = 'failed', 
               completed_at = ?
           WHERE id = ?""",
        (datetime.now().isoformat(), import_id)
    )
    conn.commit()


def get_imports(conn: sqlite3.Connection) -> list[dict]:
    """Get all imports."""
    cursor = conn.execute("SELECT * FROM _import_meta ORDER BY id DESC")
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]
