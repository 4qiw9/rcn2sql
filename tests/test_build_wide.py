"""
Tests for wide table building.
"""
import sqlite3
import tempfile
import os
import pytest

from src.build_wide import build_wide


class TestBuildWide:
    def setup_method(self):
        # Create temp database with raw tables
        self.temp_fd, self.temp_db = tempfile.mkstemp(suffix=".sqlite")
        conn = sqlite3.connect(self.temp_db)

        # Create minimal schema
        conn.execute("""
            CREATE TABLE raw_transakcja (
                id TEXT PRIMARY KEY,
                nieruchomosc_fk TEXT,
                dokument_fk TEXT,
                cena_transakcji_brutto REAL,
                data_wpisu TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE raw_nieruchomosc (
                id TEXT PRIMARY KEY,
                rodzaj_nieruchomosci TEXT,
                rodzaj_prawa_do_nieruchomosci TEXT,
                udzial_w_prawie_do_nieruchomosci TEXT,
                cena_nieruchomosci_brutto REAL,
                data_wpisu TEXT,
                dzialka_fk TEXT,
                budynek_fk TEXT,
                lokal_fk TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE raw_dokument (
                id TEXT PRIMARY KEY,
                oznaczenie_dokumentu TEXT,
                data_sporzadzenia_dokumentu TEXT,
                tworca_dokumentu TEXT
            )
        """)
        conn.execute("CREATE TABLE raw_dzialka (id TEXT PRIMARY KEY, id_dzialki TEXT, pole_powierzchni_ewidencyjnej REAL, sposob_uzytkowania TEXT, adres_dzialki_fk TEXT)")
        conn.execute("CREATE TABLE raw_budynek (id TEXT PRIMARY KEY, id_budynku TEXT, liczba_kondygnacji INT, liczba_mieszkan INT, rodzaj_budynku TEXT, adres_budynku_fk TEXT)")
        conn.execute("CREATE TABLE raw_lokal (id TEXT PRIMARY KEY, id_lokalu TEXT, numer_lokalu TEXT, funkcja_lokalu TEXT, liczba_izb INT, nr_kondygnacji INT, pow_uzytkowo_lokalu REAL, cena_lokalu_brutto REAL, adres_budynku_z_lokalem_fk TEXT)")
        conn.execute("CREATE TABLE raw_adres (id TEXT PRIMARY KEY, miejscowosc TEXT, ulica TEXT, numer_porzadkowy TEXT)")

        # Insert test data
        conn.execute("INSERT INTO raw_transakcja VALUES ('tx1', 'nier1', 'dok1', 100000.0, '2025-01-01')")
        conn.execute("INSERT INTO raw_nieruchomosc VALUES ('nier1', '1', '1', '1/1', 100000.0, '2025-01-01', NULL, NULL, NULL)")
        conn.execute("INSERT INTO raw_dokument VALUES ('dok1', 'DOC/2025', '2025-01-01', 'Notariusz')")

        conn.commit()
        conn.close()

    def teardown_method(self):
        os.close(self.temp_fd)
        os.unlink(self.temp_db)

    def test_build_wide_creates_table(self):
        result = build_wide(self.temp_db, table="test_wide", drop=True)

        assert result["table"] == "test_wide"
        assert result["row_count"] == 1

    def test_build_wide_with_limit(self):
        # Add more rows
        conn = sqlite3.connect(self.temp_db)
        conn.execute("INSERT INTO raw_transakcja VALUES ('tx2', NULL, NULL, 200000.0, '2025-02-01')")
        conn.execute("INSERT INTO raw_transakcja VALUES ('tx3', NULL, NULL, 300000.0, '2025-03-01')")
        conn.commit()
        conn.close()

        result = build_wide(self.temp_db, table="test_wide", limit=2, drop=True)

        assert result["row_count"] == 2

