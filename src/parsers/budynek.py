# parsers/budynek.py
import sqlite3
import xml.etree.ElementTree as ET
from .base import BaseParser, logger


class BudynekParser(BaseParser):
    FEATURE_TYPE = "RCN_Budynek"

    INSERT_SQL = """
    INSERT OR REPLACE INTO raw_budynek (
        id,
        id_budynku,
        liczba_kondygnacji,
        liczba_mieszkan,
        rodzaj_budynku,
        adres_budynku_fk,
        data_wpisu,
        raw_xml,
        import_id
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """

    def ensure_schema(self, conn: sqlite3.Connection) -> None:
        """Create the raw_budynek table if it doesn't exist."""
        conn.execute("""
        CREATE TABLE IF NOT EXISTS raw_budynek (
          id                      TEXT PRIMARY KEY,
          id_budynku              TEXT,
          liczba_kondygnacji      INTEGER,
          liczba_mieszkan         INTEGER,
          rodzaj_budynku          TEXT,
          adres_budynku_fk        TEXT,
          data_wpisu              DATE,
          raw_xml                 TEXT,
          import_id               INTEGER REFERENCES _import_meta(id)
        );
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_bud_adres ON raw_budynek(adres_budynku_fk);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_bud_id ON raw_budynek(id_budynku);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_bud_import ON raw_budynek(import_id);")

    def parse(self, feature_elem: ET.Element) -> tuple | None:
        """
        Return (id, id_budynku, liczba_kondygnacji, liczba_mieszkan, rodzaj_budynku,
                adres_budynku_fk, data_wpisu, raw_xml) or None to skip.
        """
        fid = self._get_gml_id(feature_elem)
        if not fid:
            logger.error("missing gml:id for budynek, skipping.")
            return None

        id_budynku = self._find_first_text(feature_elem, "idBudynku", required=False)
        liczba_kondygnacji = self._find_first_text(feature_elem, "liczbaKondygnacji", required=False)
        liczba_mieszkan = self._find_first_text(feature_elem, "liczbaMieszkań", required=False)
        rodzaj_budynku = self._find_first_text(feature_elem, "rodzajBudynku", required=False)
        adres_fk = self._href_to_id(self._find_first_href(feature_elem, "adresBudynku", required=False), "adresBudynku")

        data_wpisu = self._extract_date_from_gml_id(fid)

        raw_xml = ET.tostring(feature_elem, encoding="unicode")

        return (fid, id_budynku, liczba_kondygnacji, liczba_mieszkan, rodzaj_budynku,
                adres_fk, data_wpisu, raw_xml)
