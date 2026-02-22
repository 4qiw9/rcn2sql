# parsers/nieruchomosc.py
import sqlite3
import xml.etree.ElementTree as ET
from .base import BaseParser, logger


class NieruchomoscParser(BaseParser):
    FEATURE_TYPE = "RCN_Nieruchomosc"

    INSERT_SQL = """
    INSERT OR REPLACE INTO raw_nieruchomosc (
        id,
        rodzaj_nieruchomosci,
        rodzaj_prawa_do_nieruchomosci,
        udzial_w_prawie_do_nieruchomosci,
        cena_nieruchomosci_brutto,
        dzialka_fk,
        budynek_fk,
        lokal_fk,
        data_wpisu,
        raw_xml
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """

    def ensure_schema(self, conn: sqlite3.Connection) -> None:
        """Create the raw_nieruchomosc table if it doesn't exist."""
        conn.execute("""
        CREATE TABLE IF NOT EXISTS raw_nieruchomosc (
          id                                  TEXT PRIMARY KEY,
          rodzaj_nieruchomosci                TEXT,
          rodzaj_prawa_do_nieruchomosci       TEXT,
          udzial_w_prawie_do_nieruchomosci    TEXT,
          cena_nieruchomosci_brutto           NUMERIC,
          dzialka_fk                          TEXT,
          budynek_fk                          TEXT,
          lokal_fk                            TEXT,
          data_wpisu                          DATE,
          raw_xml                             TEXT
        );
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_nier_dzialka ON raw_nieruchomosc(dzialka_fk);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_nier_budynek ON raw_nieruchomosc(budynek_fk);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_nier_lokal ON raw_nieruchomosc(lokal_fk);")

    def parse(self, feature_elem: ET.Element) -> tuple | None:
        """
        Return (id, rodzaj_nieruchomosci, rodzaj_prawa_do_nieruchomosci,
                udzial_w_prawie_do_nieruchomosci, cena_nieruchomosci_brutto,
                dzialka_fk, budynek_fk, lokal_fk, data_wpisu, raw_xml) or None to skip.
        """
        fid = self._get_gml_id(feature_elem)
        if not fid:
            logger.error("missing gml:id for nieruchomosc, skipping.")
            return None

        rodzaj_nier = self._find_first_text(feature_elem, "rodzajNieruchomosci", required=False)
        rodzaj_prawa = self._find_first_text(feature_elem, "rodzajPrawaDoNieruchomosci", required=False)
        udzial = self._find_first_text(feature_elem, "udzialWPrawieDoNieruchomosci", required=False)
        cena_brutto = self._find_first_text(feature_elem, "cenaNieruchomosciBrutto", required=False)

        dzialka_fk = self._href_to_id(self._find_first_href(feature_elem, "dzialka", required=False), "dzialka")
        budynek_fk = self._href_to_id(self._find_first_href(feature_elem, "budynek", required=False), "budynek")
        lokal_fk = self._href_to_id(self._find_first_href(feature_elem, "lokal", required=False), "lokal")

        data_wpisu = self._extract_date_from_gml_id(fid)

        raw_xml = ET.tostring(feature_elem, encoding="unicode")

        return (fid, rodzaj_nier, rodzaj_prawa, udzial, cena_brutto,
                dzialka_fk, budynek_fk, lokal_fk, data_wpisu, raw_xml)

