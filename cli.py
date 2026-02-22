#!/usr/bin/env python3
"""
rcn2sql CLI - unified command-line interface for RCN GML to SQLite conversion.

Usage:
    python cli.py parse --gml <file.gml> --db <database.sqlite>
    python cli.py parse-dir --dir <folder> --db <database.sqlite>
    python cli.py build-wide --db <database.sqlite> --table <table_name>
    python cli.py pipeline --gml <file.gml> --db <database.sqlite>
    python cli.py imports --db <database.sqlite>
"""
import argparse
import glob
import logging
import os
import sqlite3

from src import __version__
from src.logging_config import setup_logging
from src.load_rcn import load_rcn
from src.build_wide import build_wide
from src.import_meta import get_imports, ensure_import_meta_schema

logger = logging.getLogger("rcn")


def _parse_gml_files(gml_pattern: str, db: str, batch: int, log_every: int, force: bool) -> dict:
    """
    Parse GML file(s) matching pattern into SQLite database.

    Returns dict with 'imported', 'skipped', 'files' counts.
    """
    files = glob.glob(gml_pattern) if '*' in gml_pattern else [gml_pattern]

    if not files:
        logger.warning(f"No GML files found matching: {gml_pattern}")
        return {"imported": 0, "skipped": 0, "files": 0}

    if len(files) > 1:
        logger.info(f"Found {len(files)} GML file(s)")

    total_imported = 0
    total_skipped = 0

    for gml_file in sorted(files):
        logger.info(f">>> Processing: {os.path.basename(gml_file)}")
        result = load_rcn(gml_file, db, batch, log_every, force)
        if result.get("skipped"):
            logger.warning(f"Skipped: {result.get('reason')}")
            total_skipped += 1
        else:
            records = result.get('inserted', 0)
            logger.info(f"Done: {records} records")
            total_imported += 1

    if len(files) > 1:
        logger.info("=== Summary ===")
        logger.info(f"Imported: {total_imported} file(s)")
        logger.info(f"Skipped: {total_skipped} file(s)")

    return {"imported": total_imported, "skipped": total_skipped, "files": len(files)}


def cmd_parse(args):
    """Parse GML file(s) and load into raw SQLite tables."""
    _parse_gml_files(args.gml, args.db, args.batch, args.log_every, args.force)


def cmd_build_wide(args):
    """Build denormalized wide table from raw tables."""
    result = build_wide(args.db, args.table, args.limit, args.drop, args.timeout)
    logger.info(f"Created table: {result['table']} ({result['row_count']} rows)")


def cmd_pipeline(args):
    """Run full pipeline: parse GML -> build wide table."""

    # Step 1: Parse GML files
    parse_result = _parse_gml_files(args.gml, args.db, args.batch, args.log_every, args.force)

    if parse_result["files"] == 0:
        return  # No files to process, skip building wide table

    # Step 2: Build wide table
    logger.info(">>> Building wide table...")
    result = build_wide(args.db, args.table, args.limit, drop=True, timeout=args.timeout)
    logger.info(f"Pipeline done. Wide table: {result['table']} ({result['row_count']} rows)")


def cmd_imports(args):
    """Show import history."""
    conn = sqlite3.connect(args.db)
    ensure_import_meta_schema(conn)
    imports = get_imports(conn)
    conn.close()

    if not imports:
        logger.info("No imports found.")
        return

    def format_size(size):
        if not size:
            return '-'
        if size > 1_000_000_000:
            return f"{size / 1_000_000_000:.1f}GB"
        if size > 1_000_000:
            return f"{size / 1_000_000:.1f}MB"
        return f"{size / 1_000:.0f}KB"

    logger.info(f"{'ID':<4} {'Source File':<25} {'Size':<8} {'Status':<10} {'Records':<10} {'Duration':<10} {'Date'}")
    logger.info("-" * 100)
    for imp in imports:
        size = format_size(imp.get('file_size'))
        records = imp.get('records_inserted') or '-'
        duration = f"{imp.get('duration_seconds', 0):.1f}s" if imp.get('duration_seconds') else '-'
        date = imp.get('started_at', '-')[:19] if imp.get('started_at') else '-'
        logger.info(f"{imp['id']:<4} {imp['source_file']:<25} {size:<8} {imp['status']:<10} {records:<10} {duration:<10} {date}")


def main():
    setup_logging()

    parser = argparse.ArgumentParser(
        prog="rcn2sql",
        description="RCN GML to SQLite converter"
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # parse subcommand
    p_parse = subparsers.add_parser("parse", help="Parse GML file(s) into raw SQLite tables")
    p_parse.add_argument("--gml", required=True, help="Path to GML file(s), supports glob patterns (e.g., \"data/*.gml\")")
    p_parse.add_argument("--db", default="rcn_raw.sqlite", help="Path to SQLite database")
    p_parse.add_argument("--batch", type=int, default=100000, help="Batch size for inserts")
    p_parse.add_argument("--log-every", type=int, default=500000, help="Log progress every N features")
    p_parse.add_argument("--force", action="store_true", help="Force re-import even if file was already imported")
    p_parse.set_defaults(func=cmd_parse)

    # build-wide subcommand
    p_wide = subparsers.add_parser("build-wide", help="Build denormalized wide table")
    p_wide.add_argument("--db", default="rcn_raw.sqlite", help="Path to SQLite database")
    p_wide.add_argument("--table", default="rcn_wide", help="Output table name")
    p_wide.add_argument("--limit", type=int, default=None, help="Limit rows (for testing)")
    p_wide.add_argument("--drop", action="store_true", help="Drop table if exists")
    p_wide.add_argument("--timeout", type=int, default=30, help="SQLite busy timeout (seconds)")
    p_wide.set_defaults(func=cmd_build_wide)

    # pipeline subcommand (parse + build-wide)
    p_pipe = subparsers.add_parser("pipeline", help="Run full pipeline: parse -> build-wide")
    p_pipe.add_argument("--gml", required=True, help="Path to GML file(s), supports glob patterns (e.g., \"data/*.gml\")")
    p_pipe.add_argument("--db", default="rcn_raw.sqlite", help="Path to SQLite database")
    p_pipe.add_argument("--batch", type=int, default=100000, help="Batch size for inserts")
    p_pipe.add_argument("--log-every", type=int, default=500000, help="Log progress every N features")
    p_pipe.add_argument("--table", default="rcn_wide", help="Output wide table name")
    p_pipe.add_argument("--limit", type=int, default=None, help="Limit wide table rows (for testing)")
    p_pipe.add_argument("--timeout", type=int, default=30, help="SQLite busy timeout (seconds)")
    p_pipe.add_argument("--force", action="store_true", help="Force re-import even if file was already imported")
    p_pipe.set_defaults(func=cmd_pipeline)

    # imports subcommand
    p_imports = subparsers.add_parser("imports", help="Show import history")
    p_imports.add_argument("--db", default="rcn_raw.sqlite", help="Path to SQLite database")
    p_imports.set_defaults(func=cmd_imports)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

