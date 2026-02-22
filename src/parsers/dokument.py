# parsers/dokument.py
import sqlite3
import xml.etree.ElementTree as ET
from .base import BaseParser, logger


class DokumentParser(BaseParser):
    FEATURE_TYPE = "RCN_Dokument"

    INSERT_SQL = """
    INSERT OR REPLACE INTO raw_dokument (
        id,
        oznaczenie_dokumentu,
        data_sporzadzenia_dokumentu,
        tworca_dokumentu,
        data_wpisu,
        raw_xml
    ) VALUES (?, ?, ?, ?, ?, ?);
    """

    def ensure_schema(self, conn: sqlite3.Connection) -> None:
        """Create the raw_dokument table if it doesn't exist."""
        conn.execute("""
        CREATE TABLE IF NOT EXISTS raw_dokument (
          id                              TEXT PRIMARY KEY,
          oznaczenie_dokumentu            TEXT,
          data_sporzadzenia_dokumentu     DATE,
          tworca_dokumentu                TEXT,
          data_wpisu                      DATE,
          raw_xml                         TEXT
        );
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_dok_oznaczenie ON raw_dokument(oznaczenie_dokumentu);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_dok_data ON raw_dokument(data_sporzadzenia_dokumentu);")

    def parse(self, feature_elem: ET.Element) -> tuple | None:
        """
        Return (id, oznaczenie_dokumentu, data_sporzadzenia_dokumentu, tworca_dokumentu,
                data_wpisu, raw_xml) or None to skip.
        """
        fid = self._get_gml_id(feature_elem)
        if not fid:
            logger.error("missing gml:id for dokument, skipping.")
            return None

        oznaczenie = self._find_first_text(feature_elem, "oznaczenieDokumentu", required=False)
        data_sporzadzenia = self._find_first_text(feature_elem, "dataSporzadzeniaDokumentu", required=False)
        tworca = self._find_first_text(feature_elem, "tworcaDokumentu", required=False)
        data_wpisu = self._extract_date_from_gml_id(fid)

        raw_xml = ET.tostring(feature_elem, encoding="unicode")

        return (fid, oznaczenie, data_sporzadzenia, tworca, data_wpisu, raw_xml)

