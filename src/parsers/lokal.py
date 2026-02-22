# parsers/lokal.py
import sqlite3
import xml.etree.ElementTree as ET
from .base import BaseParser, logger


class LokalParser(BaseParser):
    FEATURE_TYPE = "RCN_Lokal"

    INSERT_SQL = """
    INSERT OR REPLACE INTO raw_lokal (
        id, 
        id_lokalu,
        numer_lokalu,
        funkcja_lokalu,
        liczba_izb,
        nr_kondygnacji,
        pow_uzytkowo_lokalu,
        cena_lokalu_brutto,
        adres_budynku_z_lokalem_fk,
        data_wpisu,
        raw_xml,
        import_id
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """

    def ensure_schema(self, conn: sqlite3.Connection) -> None:
        """Create the raw_lokal table if it doesn't exist."""
        conn.execute("""
        CREATE TABLE IF NOT EXISTS raw_lokal (
          id                          TEXT PRIMARY KEY,
          id_lokalu                   TEXT,
          numer_lokalu                TEXT,
          funkcja_lokalu              TEXT,
          liczba_izb                  INTEGER,
          nr_kondygnacji              INTEGER,
          pow_uzytkowo_lokalu         NUMERIC,
          cena_lokalu_brutto          NUMERIC,
          adres_budynku_z_lokalem_fk  TEXT,
          data_wpisu                  DATE,
          raw_xml                     TEXT,
          import_id                   INTEGER REFERENCES _import_meta(id)
        );
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_lok_adres ON raw_lokal(adres_budynku_z_lokalem_fk);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_lok_id ON raw_lokal(id_lokalu);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_lok_numer ON raw_lokal(numer_lokalu);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_lok_import ON raw_lokal(import_id);")

    def _extract_numer_lokalu(self, id_lokalu: str | None) -> str | None:
        """
        Extract numer_lokalu from idLokalu.
        Example: '146519_8.0204.4/3.7_BUD.21_LOK' -> '21'
        Format is usually: '...BUD.XXX_LOK' where XXX is the numer_lokalu
        """
        if not id_lokalu:
            return None

        # Look for pattern 'BUD.XXX' where XXX is the number
        try:
            # Find 'BUD.' in the string
            bud_index = id_lokalu.find("BUD.")
            if bud_index == -1:
                return None

            # Extract everything after 'BUD.'
            after_bud = id_lokalu[bud_index + 4:]  # skip 'BUD.'

            # Find the first underscore or dot to get just the number
            for i, char in enumerate(after_bud):
                if char in ('_', '.'):
                    return after_bud[:i].strip()

            # If no delimiter found, return what's left (unlikely but safe)
            return after_bud.strip() if after_bud else None
        except (IndexError, AttributeError):
            logger.error(f"cannot extract numer_lokalu from: {id_lokalu}")
            return None

    def parse(self, feature_elem: ET.Element) -> tuple | None:
        """
        Return (id, id_lokalu, numer_lokalu, funkcja_lokalu, liczba_izb, nr_kondygnacji,
                pow_uzytkowo_lokalu, cena_lokalu_brutto, adres_budynku_z_lokalem_fk,
                data_wpisu, raw_xml) or None to skip.
        """
        fid = self._get_gml_id(feature_elem)
        if not fid:
            logger.error("missing gml:id for lokal, skipping.")
            return None

        id_lokalu = self._find_first_text(feature_elem, "idLokalu", required=False)
        numer_lokalu = self._extract_numer_lokalu(id_lokalu)
        funkcja_lokalu = self._find_first_text(feature_elem, "funkcjaLokalu", required=False)
        liczba_izb = self._find_first_text(feature_elem, "liczbaIzb", required=False)
        nr_kondygnacji = self._find_first_text(feature_elem, "nrKondygnacji", required=False)
        pow_uzytkowo = self._find_first_text(feature_elem, "powUzytkowaLokalu", required=False)
        cena_brutto = self._find_first_text(feature_elem, "cenaLokaluBrutto", required=False)
        adres_fk = self._href_to_id(self._find_first_href(feature_elem, "adresBudynkuZLokalem", required=False), "adresBudynkuZLokalem")
        data_wpisu = self._extract_date_from_gml_id(fid)

        raw_xml = ET.tostring(feature_elem, encoding="unicode")

        return (fid, id_lokalu, numer_lokalu, funkcja_lokalu, liczba_izb, nr_kondygnacji,
                pow_uzytkowo, cena_brutto, adres_fk, data_wpisu, raw_xml)
