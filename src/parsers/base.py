import logging
import sqlite3
from abc import ABC, abstractmethod
import xml.etree.ElementTree as ET
from datetime import date

# Logger for all parsers to use. Configured via setup_logging().
logger = logging.getLogger("rcn")


class BaseParser(ABC):
    """
    Abstract base class for GML feature parsers.

    Helper methods (_local, _get_gml_id, _find_first_href etd.) provide common
    XML parsing utilities used by all parsers to extract data from GML elements
    """

    XLINK_NS = "http://www.w3.org/1999/xlink"

    def __init__(self, config):
        self.config = config

    @abstractmethod
    def ensure_schema(self, conn: sqlite3.Connection) -> None:
        """ Create the necessary tables and indexes if they don't exist """
        raise NotImplementedError

    @abstractmethod
    def parse(self, feature_elem: ET.Element):
        """ Return a tuple of values to be inserted into the database, or None to skip """
        raise NotImplementedError

    def insert_many(self, conn: sqlite3.Connection, rows) -> int:
        if not rows:
            return 0
        conn.executemany(self.INSERT_SQL, rows)
        return len(rows)

    def _local(self, tag: str) -> str:
        """
        Return tag name without XML namespace.
        Example: '{uri}name' -> 'name'
        """
        if tag and "}" in tag:
            return tag.split("}", 1)[1]
        return tag

    def _get_gml_id(self, elem: ET.Element) -> str | None:
        """
        Get gml:id from an element (ElementTree stores it as '{gml-uri}id').
        """
        for attr_name, attr_value in elem.attrib.items():
            if attr_name.endswith("}id") and attr_value:
                return attr_value

        value = elem.attrib.get("id")
        if value:
            return value.strip()
        else:
            logger.error(f"missing gml:id for element, skipping. Element: {ET.tostring(elem, encoding='unicode')}")
            return None

    def _find_first_href(self, elem: ET.Element, field_localname: str, required: bool = True) -> str | None:
        """
        Find xlink:href value inside the first descendant with a given local tag name.
        If required=False, return None silently when href is missing.
        If required=True, log an error when href is missing.
        """
        xlink_href_attr = f"{{{self.XLINK_NS}}}href"

        for node in elem.iter():
            if self._local(node.tag) != field_localname:
                continue

            href = node.attrib.get(xlink_href_attr)
            if href:
                return href.strip()

            href = node.attrib.get("href")
            if href:
                return href.strip()
            else:
                if required:
                    logger.error(f"missing xlink:href for {field_localname} reference, skipping. Element: {ET.tostring(node, encoding='unicode')}")
                return None

        return None

    def _href_to_id(self, href: str | None, field_name: str = "unknown") -> str | None:
        """
        Convert href to id.
        Example: '#ABC' or 'file.gml#ABC' -> 'ABC'
        Returns None silently if href is None.
        """
        if not href:
            return None

        href = href.strip()
        if "#" in href:
            after_hash = href.split("#", 1)[1]
            if after_hash:
                return after_hash.strip()
            else:
                logger.error(f"empty id in href for {field_name}, skipping. href: {href}")
                return None

        return href

    def _find_first_text(self, elem: ET.Element, child_localname: str, required: bool = True) -> str | None:
        """
        Return the first non-empty text of a descendant element by local tag name.
        If required=False, return None silently when text is missing or empty.
        If required=True, log an error when text is missing.
        """
        for node in elem.iter():
            if self._local(node.tag) == child_localname:
                txt = (node.text or "").strip()
                if txt:
                    return txt
                else:
                    if required:
                        logger.error(f"missing {child_localname} text for element, skipping. Element: {ET.tostring(node, encoding='unicode')}")
                    return None
        return None

    def _extract_date_from_gml_id(self, fid: str) -> str | None:
        """
        Extract date from gml:id.
        Returns ISO date string 'YYYY-MM-DD' or None.
        """
        try:
            tail = fid.rsplit("_", 1)[1]
            d = tail.split("T", 1)[0]
            date.fromisoformat(d)
            return d
        except (IndexError, ValueError):
            logger.error(f"missing/invalid timestamp in gml:id: {fid}, skipping")
            return None
