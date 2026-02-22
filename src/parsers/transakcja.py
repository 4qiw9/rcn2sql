# parsers/transakcja.py
import sqlite3
import xml.etree.ElementTree as ET
from .base import BaseParser, logger


class TransakcjaParser(BaseParser):
    FEATURE_TYPE = "RCN_Transakcja"

    INSERT_SQL = """
    INSERT OR REPLACE INTO raw_transakcja (
        id, 
        nieruchomosc_fk, 
        dokument_fk, 
        cena_transakcji_brutto,
        data_wpisu,
        raw_xml,
        import_id
    ) VALUES (?, ?, ?, ?, ?, ?, ?);
    """

    def ensure_schema(self, conn: sqlite3.Connection) -> None:
        """Create the raw_transakcja table if it doesn't exist."""
        conn.execute("""
        CREATE TABLE IF NOT EXISTS raw_transakcja (
          id                TEXT PRIMARY KEY,
          nieruchomosc_fk   TEXT,
          dokument_fk       TEXT,
          cena_transakcji_brutto NUMERIC,
          data_wpisu        DATE,
          raw_xml           TEXT,
          import_id         INTEGER REFERENCES _import_meta(id)
        );
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tx_nier ON raw_transakcja(nieruchomosc_fk);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tx_doc  ON raw_transakcja(dokument_fk);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tx_import ON raw_transakcja(import_id);")

    def parse(self, feature_elem: ET.Element) -> tuple | None:
        """
        Return tuple or None to skip.
        """
        fid = self._get_gml_id(feature_elem)
        if not fid:
            logger.error("missing gml:id for transakcja, skipping.")
            return None

        nier_fk = self._href_to_id(self._find_first_href(feature_elem, "nieruchomosc"), "nieruchomosc")
        doc_fk = self._href_to_id(self._find_first_href(feature_elem, "podstawaPrawna", required=False), "podstawaPrawna")
        cena = self._find_first_text(feature_elem, "cenaTransakcjiBrutto", required=False)
        data_wpisu = self._extract_date_from_gml_id(fid)

        raw_xml = ET.tostring(feature_elem, encoding="unicode")
        return (fid, nier_fk, doc_fk, cena, data_wpisu, raw_xml)
