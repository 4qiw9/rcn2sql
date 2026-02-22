# parsers/adres.py
import sqlite3
import xml.etree.ElementTree as ET
from .base import BaseParser, logger


class AdresParser(BaseParser):
    FEATURE_TYPE = "RCN_Adres"

    INSERT_SQL = """
    INSERT OR REPLACE INTO raw_adres (
        id,
        miejscowosc,
        ulica,
        numer_porzadkowy,
        data_wpisu,
        raw_xml
    ) VALUES (?, ?, ?, ?, ?, ?);
    """

    def ensure_schema(self, conn: sqlite3.Connection) -> None:
        """Create the raw_adres table if it doesn't exist."""
        conn.execute("""
        CREATE TABLE IF NOT EXISTS raw_adres (
          id                  TEXT PRIMARY KEY,
          miejscowosc         TEXT,
          ulica               TEXT,
          numer_porzadkowy    TEXT,
          data_wpisu          DATE,
          raw_xml             TEXT
        );
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_adr_miejscowosc ON raw_adres(miejscowosc);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_adr_ulica ON raw_adres(ulica);")

    def parse(self, feature_elem: ET.Element) -> tuple | None:
        """
        Return (id, miejscowosc, ulica, numer_porzadkowy, data_wpisu, raw_xml) or None to skip.
        """
        fid = self._get_gml_id(feature_elem)
        if not fid:
            logger.error("missing gml:id for adres, skipping.")
            return None

        miejscowosc = self._find_first_text(feature_elem, "miejscowosc", required=False)
        ulica = self._find_first_text(feature_elem, "ulica", required=False)
        numer_porzadkowy = self._find_first_text(feature_elem, "numerPorzadkowy", required=False)
        data_wpisu = self._extract_date_from_gml_id(fid)

        raw_xml = ET.tostring(feature_elem, encoding="unicode")

        return (fid, miejscowosc, ulica, numer_porzadkowy, data_wpisu, raw_xml)

