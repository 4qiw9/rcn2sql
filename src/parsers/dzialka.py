# parsers/dzialka.py
import sqlite3
import xml.etree.ElementTree as ET
from .base import BaseParser, logger


class DzialkaParser(BaseParser):
    FEATURE_TYPE = "RCN_Dzialka"

    INSERT_SQL = """
    INSERT OR REPLACE INTO raw_dzialka (
        id,
        id_dzialki,
        pole_powierzchni_ewidencyjnej,
        sposob_uzytkowania,
        adres_dzialki_fk,
        data_wpisu,
        raw_xml,
        import_id
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """

    def ensure_schema(self, conn: sqlite3.Connection) -> None:
        """Create the raw_dzialka table if it doesn't exist."""
        conn.execute("""
        CREATE TABLE IF NOT EXISTS raw_dzialka (
          id                              TEXT PRIMARY KEY,
          id_dzialki                      TEXT,
          pole_powierzchni_ewidencyjnej   NUMERIC,
          sposob_uzytkowania              TEXT,
          adres_dzialki_fk                TEXT,
          data_wpisu                      DATE,
          raw_xml                         TEXT,
          import_id                       INTEGER REFERENCES _import_meta(id)
        );
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_dzi_adres ON raw_dzialka(adres_dzialki_fk);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_dzi_id ON raw_dzialka(id_dzialki);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_dzi_import ON raw_dzialka(import_id);")

    def parse(self, feature_elem: ET.Element) -> tuple | None:
        """
        Return (id, id_dzialki, pole_powierzchni_ewidencyjnej, sposob_uzytkowania,
                adres_dzialki_fk, data_wpisu, raw_xml) or None to skip.
        """
        fid = self._get_gml_id(feature_elem)
        if not fid:
            logger.error("missing gml:id for dzialka, skipping.")
            return None

        id_dzialki = self._find_first_text(feature_elem, "idDzialki", required=False)
        pole_pow = self._find_first_text(feature_elem, "polePowierzchniEwidencyjnej", required=False)
        sposob_uzytkowania = self._find_first_text(feature_elem, "sposobUzytkowania", required=False)
        adres_fk = self._href_to_id(self._find_first_href(feature_elem, "adresDzialki", required=False), "adresDzialki")

        data_wpisu = self._extract_date_from_gml_id(fid)

        raw_xml = ET.tostring(feature_elem, encoding="unicode")

        return (fid, id_dzialki, pole_pow, sposob_uzytkowania,
                adres_fk, data_wpisu, raw_xml)
