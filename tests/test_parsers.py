"""
Tests for RCN parsers.
"""
import xml.etree.ElementTree as ET
import pytest

from src.parsers.transakcja import TransakcjaParser
from src.parsers.adres import AdresParser
from src.parsers.dokument import DokumentParser
from src.parsers.nieruchomosc import NieruchomoscParser
from src.parsers.dzialka import DzialkaParser
from src.parsers.budynek import BudynekParser
from src.parsers.lokal import LokalParser


class TestTransakcjaParser:
    def setup_method(self):
        self.parser = TransakcjaParser(config={})

    def test_parse_valid_transakcja(self):
        xml_str = """
        <rcn:RCN_Transakcja xmlns:rcn="urn:rcn" xmlns:gml="http://www.opengis.net/gml/3.2" 
                            xmlns:xlink="http://www.w3.org/1999/xlink"
                            gml:id="PL.PZGiK.1234_00000-000_2025-01-01T00-00-00">
            <rcn:cenaTransakcjiBrutto>500000.00</rcn:cenaTransakcjiBrutto>
            <rcn:podstawaPrawna xlink:href="#PL.PZGiK.1234_11111-111_2025-01-01T00-00-00"/>
            <rcn:nieruchomosc xlink:href="#PL.PZGiK.1234_22222-222_2025-01-01T00-00-00"/>
        </rcn:RCN_Transakcja>
        """
        elem = ET.fromstring(xml_str)
        result = self.parser.parse(elem)

        assert result is not None
        assert result[0] == "PL.PZGiK.1234_00000-000_2025-01-01T00-00-00"  # id
        assert float(result[3]) == 500000.00  # cena (may be string or float)

    def test_parse_missing_gml_id_returns_none(self):
        xml_str = """
        <rcn:RCN_Transakcja xmlns:rcn="urn:rcn">
            <rcn:cenaTransakcjiBrutto>100.00</rcn:cenaTransakcjiBrutto>
        </rcn:RCN_Transakcja>
        """
        elem = ET.fromstring(xml_str)
        result = self.parser.parse(elem)

        assert result is None


class TestAdresParser:
    def setup_method(self):
        self.parser = AdresParser(config={})

    def test_parse_valid_adres(self):
        xml_str = """
        <rcn:RCN_Adres xmlns:rcn="urn:rcn" xmlns:gml="http://www.opengis.net/gml/3.2"
                       gml:id="PL.PZGiK.1234_55555-555_2025-01-01T00-00-00">
            <rcn:miejscowosc>Warszawa</rcn:miejscowosc>
            <rcn:ulica>Marszałkowska</rcn:ulica>
            <rcn:numerPorzadkowy>10</rcn:numerPorzadkowy>
        </rcn:RCN_Adres>
        """
        elem = ET.fromstring(xml_str)
        result = self.parser.parse(elem)

        assert result is not None
        assert result[1] == "Warszawa"  # miejscowosc
        assert result[2] == "Marszałkowska"  # ulica
        assert result[3] == "10"  # numer


class TestDokumentParser:
    def setup_method(self):
        self.parser = DokumentParser(config={})

    def test_parse_valid_dokument(self):
        xml_str = """
        <rcn:RCN_Dokument xmlns:rcn="urn:rcn" xmlns:gml="http://www.opengis.net/gml/3.2"
                          gml:id="PL.PZGiK.1234_00000-000_2025-01-01T00-00-00">
            <rcn:oznaczenieDokumentu>1234/2025</rcn:oznaczenieDokumentu>
            <rcn:dataSporzadzeniaDokumentu>2025-01-01</rcn:dataSporzadzeniaDokumentu>
            <rcn:tworcaDokumentu>Notariusz XYZ</rcn:tworcaDokumentu>
        </rcn:RCN_Dokument>
        """
        elem = ET.fromstring(xml_str)
        result = self.parser.parse(elem)

        assert result is not None
        assert result[0] == "PL.PZGiK.1234_00000-000_2025-01-01T00-00-00"
        assert result[1] == "1234/2025"
        assert result[2] == "2025-01-01"
        assert result[3] == "Notariusz XYZ"


class TestNieruchomoscParser:
    def setup_method(self):
        self.parser = NieruchomoscParser(config={})

    def test_parse_valid_nieruchomosc(self):
        xml_str = """
        <rcn:RCN_Nieruchomosc xmlns:rcn="urn:rcn" xmlns:gml="http://www.opengis.net/gml/3.2"
                              xmlns:xlink="http://www.w3.org/1999/xlink"
                              gml:id="PL.PZGiK.1234_11111-111_2025-01-01T00-00-00">
            <rcn:rodzajNieruchomosci>4</rcn:rodzajNieruchomosci>
            <rcn:rodzajPrawaDoNieruchomosci>3</rcn:rodzajPrawaDoNieruchomosci>
            <rcn:udzialWPrawieDoNieruchomosci>1/1</rcn:udzialWPrawieDoNieruchomosci>
            <rcn:cenaNieruchomosciBrutto>500000.00</rcn:cenaNieruchomosciBrutto>
            <rcn:dzialka xlink:href="#dzialka_1"/>
            <rcn:budynek xlink:href="#budynek_1"/>
            <rcn:lokal xlink:href="#lokal_1"/>
        </rcn:RCN_Nieruchomosc>
        """
        elem = ET.fromstring(xml_str)
        result = self.parser.parse(elem)

        assert result is not None
        assert result[0] == "PL.PZGiK.1234_11111-111_2025-01-01T00-00-00"
        assert result[1] == "4"
        assert result[3] == "1/1"


class TestDzialkaParser:
    def setup_method(self):
        self.parser = DzialkaParser(config={})

    def test_parse_valid_dzialka(self):
        xml_str = """
        <rcn:RCN_Dzialka xmlns:rcn="urn:rcn" xmlns:gml="http://www.opengis.net/gml/3.2"
                         xmlns:xlink="http://www.w3.org/1999/xlink"
                         gml:id="PL.PZGiK.1234_22222-222_2025-01-01T00-00-00">
            <rcn:idDzialki>146519_8.0306.31</rcn:idDzialki>
            <rcn:polePowierzchniEwidencyjnej>8474.00</rcn:polePowierzchniEwidencyjnej>
            <rcn:sposobUzytkowania>3</rcn:sposobUzytkowania>
            <rcn:adresDzialki xlink:href="#adres_1"/>
        </rcn:RCN_Dzialka>
        """
        elem = ET.fromstring(xml_str)
        result = self.parser.parse(elem)

        assert result is not None
        assert result[0] == "PL.PZGiK.1234_22222-222_2025-01-01T00-00-00"
        assert result[1] == "146519_8.0306.31"
        assert result[2] == "8474.00"


class TestBudynekParser:
    def setup_method(self):
        self.parser = BudynekParser(config={})

    def test_parse_valid_budynek(self):
        xml_str = """
        <rcn:RCN_Budynek xmlns:rcn="urn:rcn" xmlns:gml="http://www.opengis.net/gml/3.2"
                         xmlns:xlink="http://www.w3.org/1999/xlink"
                         gml:id="PL.PZGiK.1234_33333-333_2025-01-01T00-00-00">
            <rcn:idBudynku>122222_8.0306.24_BUD</rcn:idBudynku>
            <rcn:liczbaKondygnacji>5</rcn:liczbaKondygnacji>
            <rcn:rodzajBudynku>110</rcn:rodzajBudynku>
            <rcn:adresBudynku xlink:href="#adres_1"/>
        </rcn:RCN_Budynek>
        """
        elem = ET.fromstring(xml_str)
        result = self.parser.parse(elem)

        assert result is not None
        assert result[0] == "PL.PZGiK.1234_33333-333_2025-01-01T00-00-00"
        assert result[1] == "122222_8.0306.24_BUD"
        assert result[2] == "5"
        assert result[4] == "110"


class TestLokalParser:
    def setup_method(self):
        self.parser = LokalParser(config={})

    def test_parse_valid_lokal(self):
        xml_str = """
        <rcn:RCN_Lokal xmlns:rcn="urn:rcn" xmlns:gml="http://www.opengis.net/gml/3.2"
                       xmlns:xlink="http://www.w3.org/1999/xlink"
                       gml:id="PL.PZGiK.1234_44444-444_2025-01-01T00-00-00">
            <rcn:idLokalu>122222_8.0306.24_BUD.21_LOK</rcn:idLokalu>
            <rcn:funkcjaLokalu>1</rcn:funkcjaLokalu>
            <rcn:liczbaIzb>3</rcn:liczbaIzb>
            <rcn:nrKondygnacji>5</rcn:nrKondygnacji>
            <rcn:powUzytkowaLokalu>54.90</rcn:powUzytkowaLokalu>
            <rcn:cenaLokaluBrutto>500000.00</rcn:cenaLokaluBrutto>
            <rcn:adresBudynkuZLokalem xlink:href="#adres_1"/>
        </rcn:RCN_Lokal>
        """
        elem = ET.fromstring(xml_str)
        result = self.parser.parse(elem)

        assert result is not None
        assert result[0] == "PL.PZGiK.1234_44444-444_2025-01-01T00-00-00"
        assert result[1] == "122222_8.0306.24_BUD.21_LOK"
        assert result[2] == "21"  # numer_lokalu extracted from idLokalu
        assert result[3] == "1"   # funkcja_lokalu
        assert result[4] == "3"   # liczba_izb

