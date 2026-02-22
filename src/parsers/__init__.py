"""
RCN parsers package.
"""
from src.parsers.transakcja import TransakcjaParser
from src.parsers.dokument import DokumentParser
from src.parsers.nieruchomosc import NieruchomoscParser
from src.parsers.dzialka import DzialkaParser
from src.parsers.budynek import BudynekParser
from src.parsers.lokal import LokalParser
from src.parsers.adres import AdresParser

__all__ = [
    "TransakcjaParser",
    "DokumentParser",
    "NieruchomoscParser",
    "DzialkaParser",
    "BudynekParser",
    "LokalParser",
    "AdresParser",
]

