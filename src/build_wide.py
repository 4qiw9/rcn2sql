#!/usr/bin/env python3
import argparse
import logging
import sqlite3
import time


logger = logging.getLogger("rcn")


def build_select_sql(limit: int | None) -> str:
    base_sql = """
    SELECT
        tx.id AS transakcja_id,
        tx.nieruchomosc_fk,
        tx.dokument_fk,
        tx.cena_transakcji_brutto,
        tx.data_wpisu AS transakcja_data_wpisu,
        tx.import_id,

        nier.id AS nieruchomosc_id,
        nier.rodzaj_nieruchomosci,
        nier.rodzaj_prawa_do_nieruchomosci,
        nier.udzial_w_prawie_do_nieruchomosci,
        nier.cena_nieruchomosci_brutto,
        nier.data_wpisu AS nieruchomosc_data_wpisu,

        dok.id AS dokument_id,
        dok.oznaczenie_dokumentu,
        dok.data_sporzadzenia_dokumentu,
        dok.tworca_dokumentu,

        dzi.id AS dzialka_id,
        dzi.id_dzialki,
        dzi.pole_powierzchni_ewidencyjnej,
        dzi.sposob_uzytkowania,

        bud.id AS budynek_id,
        bud.id_budynku,
        bud.liczba_kondygnacji,
        bud.liczba_mieszkan,
        bud.rodzaj_budynku,

        lok.id AS lokal_id,
        lok.id_lokalu,
        lok.numer_lokalu,
        lok.funkcja_lokalu,
        lok.liczba_izb,
        lok.nr_kondygnacji,
        lok.pow_uzytkowo_lokalu,
        lok.cena_lokalu_brutto,

        adr_dzi.id AS adres_dzialki_id,
        adr_dzi.miejscowosc AS adres_dzialki_miejscowosc,
        adr_dzi.ulica AS adres_dzialki_ulica,
        adr_dzi.numer_porzadkowy AS adres_dzialki_numer,

        adr_bud.id AS adres_budynku_id,
        adr_bud.miejscowosc AS adres_budynku_miejscowosc,
        adr_bud.ulica AS adres_budynku_ulica,
        adr_bud.numer_porzadkowy AS adres_budynku_numer,

        adr_lok.id AS adres_lokalu_id,
        adr_lok.miejscowosc AS adres_lokalu_miejscowosc,
        adr_lok.ulica AS adres_lokalu_ulica,
        adr_lok.numer_porzadkowy AS adres_lokalu_numer
    FROM raw_transakcja tx
    LEFT JOIN raw_nieruchomosc nier ON tx.nieruchomosc_fk = nier.id
    LEFT JOIN raw_dokument dok ON tx.dokument_fk = dok.id
    LEFT JOIN raw_nieruchomosc_dzialka nd ON nier.id = nd.nieruchomosc_id
    LEFT JOIN raw_dzialka dzi ON nd.dzialka_id = dzi.id
    LEFT JOIN raw_nieruchomosc_budynek nb ON nier.id = nb.nieruchomosc_id
    LEFT JOIN raw_budynek bud ON nb.budynek_id = bud.id
    LEFT JOIN raw_nieruchomosc_lokal nl ON nier.id = nl.nieruchomosc_id
    LEFT JOIN raw_lokal lok ON nl.lokal_id = lok.id
    LEFT JOIN raw_adres adr_dzi ON dzi.adres_dzialki_fk = adr_dzi.id
    LEFT JOIN raw_adres adr_bud ON bud.adres_budynku_fk = adr_bud.id
    LEFT JOIN raw_adres adr_lok ON lok.adres_budynku_z_lokalem_fk = adr_lok.id
    """

    if limit is not None:
        return base_sql + f"\nLIMIT {int(limit)}"
    return base_sql


def create_indexes(conn: sqlite3.Connection, table: str) -> None:
    conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_transakcja_id ON {table}(transakcja_id);")
    conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_nieruchomosc_id ON {table}(nieruchomosc_id);")
    conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_dzialka_id ON {table}(dzialka_id);")
    conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_budynek_id ON {table}(budynek_id);")
    conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_lokal_id ON {table}(lokal_id);")
    conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_import_id ON {table}(import_id);")


def build_wide(db_path: str, table: str = "rcn_wide", limit: int | None = None,
               drop: bool = False, timeout: int = 30) -> dict:
    """
    Build denormalized wide table from raw tables.

    Args:
        db_path: Path to SQLite database
        table: Output table name
        limit: Limit rows (for testing)
        drop: Drop table if exists
        timeout: SQLite busy timeout in seconds

    Returns:
        dict with statistics: table, row_count
    """
    logger.info("=" * 60)
    logger.info("RCN Build Wide started")
    logger.info("=" * 60)
    logger.info(f"Database: {db_path}")
    logger.info(f"Table: {table}")
    logger.info(f"Limit: {limit}")
    logger.info(f"Drop existing: {drop}")
    logger.info(f"Timeout: {timeout}s")

    start = time.time()
    conn = sqlite3.connect(db_path, timeout=timeout)
    conn.execute(f"PRAGMA busy_timeout = {timeout * 1000};")

    try:
        if drop:
            conn.execute(f"DROP TABLE IF EXISTS {table};")
            logger.info(f"Dropped existing table: {table}")

        logger.info("Building wide table...")
        select_sql = build_select_sql(limit)
        conn.execute(f"CREATE TABLE {table} AS {select_sql};")
        logger.info("Creating indexes...")
        create_indexes(conn, table)
        conn.commit()

        row_count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        elapsed = time.time() - start

        logger.info("=" * 60)
        logger.info(f"Done. table={table}, rows={row_count}, time={elapsed:.1f}s")

        return {
            "table": table,
            "row_count": row_count,
            "elapsed": elapsed,
        }
    except sqlite3.OperationalError as exc:
        logger.error(f"SQLite error: {exc}")
        raise SystemExit(f"SQLite error: {exc}. If database is locked, close other connections and retry.")
    finally:
        conn.close()


def main() -> None:
    from logging_config import setup_logging
    setup_logging()

    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="rcn_raw.sqlite", help="Path to SQLite DB")
    ap.add_argument("--table", default="rcn_wide", help="Output table name")
    ap.add_argument("--limit", type=int, default=None, help="Limit rows (useful for testing)")
    ap.add_argument("--drop", action="store_true", help="Drop table if exists before creating")
    ap.add_argument("--timeout", type=int, default=30, help="SQLite busy timeout in seconds")
    args = ap.parse_args()

    result = build_wide(args.db, args.table, args.limit, args.drop, args.timeout)
    print(f"Created table: {result['table']} ({result['row_count']} rows)")


if __name__ == "__main__":
    main()

