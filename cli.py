#!/usr/bin/env python3
"""
rcn2sql CLI - unified command-line interface for RCN GML to SQLite conversion.

Usage:
    python cli.py parse --gml <file.gml> --db <database.sqlite>
    python cli.py build-wide --db <database.sqlite> --table <table_name>
    python cli.py pipeline --gml <file.gml> --db <database.sqlite>
"""
import argparse

from src import __version__
from src.logging_config import setup_logging
from src.load_rcn import load_rcn
from src.build_wide import build_wide


def cmd_parse(args):
    """Parse GML file and load into raw SQLite tables."""
    load_rcn(args.gml, args.db, args.batch, args.log_every)


def cmd_build_wide(args):
    """Build denormalized wide table from raw tables."""
    result = build_wide(args.db, args.table, args.limit, args.drop, args.timeout)
    print(f"Created table: {result['table']} ({result['row_count']} rows)")


def cmd_pipeline(args):
    """Run full pipeline: parse GML -> build wide table."""

    # Step 1: Parse GML
    load_rcn(args.gml, args.db, args.batch, args.log_every)

    # Step 2: Build wide table
    result = build_wide(args.db, args.table, args.limit, drop=True, timeout=args.timeout)
    print(f"Pipeline done. Wide table: {result['table']} ({result['row_count']} rows)")


def main():
    setup_logging()

    parser = argparse.ArgumentParser(
        prog="rcn2sql",
        description="RCN GML to SQLite converter"
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # parse subcommand
    p_parse = subparsers.add_parser("parse", help="Parse GML file into raw SQLite tables")
    p_parse.add_argument("--gml", required=True, help="Path to RCN GML file")
    p_parse.add_argument("--db", default="rcn_raw.sqlite", help="Path to SQLite database")
    p_parse.add_argument("--batch", type=int, default=100000, help="Batch size for inserts")
    p_parse.add_argument("--log-every", type=int, default=500000, help="Log progress every N features")
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
    p_pipe.add_argument("--gml", required=True, help="Path to RCN GML file")
    p_pipe.add_argument("--db", default="rcn_raw.sqlite", help="Path to SQLite database")
    p_pipe.add_argument("--batch", type=int, default=100000, help="Batch size for inserts")
    p_pipe.add_argument("--log-every", type=int, default=500000, help="Log progress every N features")
    p_pipe.add_argument("--table", default="rcn_wide", help="Output wide table name")
    p_pipe.add_argument("--limit", type=int, default=None, help="Limit wide table rows (for testing)")
    p_pipe.add_argument("--timeout", type=int, default=30, help="SQLite busy timeout (seconds)")
    p_pipe.set_defaults(func=cmd_pipeline)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

