#!/usr/bin/env python3
import argparse
import logging
import sqlite3
import time
import xml.etree.ElementTree as ET

from src.logging_config import setup_logging
from src.utils import local
from src.parsers.transakcja import TransakcjaParser
from src.parsers.lokal import LokalParser
from src.parsers.dokument import DokumentParser
from src.parsers.nieruchomosc import NieruchomoscParser
from src.parsers.dzialka import DzialkaParser
from src.parsers.adres import AdresParser
from src.parsers.budynek import BudynekParser


# Parsers composition: add parsers explicitly.
_parsers_instances = [
    TransakcjaParser(config={}),
    LokalParser(config={}),
    DokumentParser(config={}),
    NieruchomoscParser(config={}),
    DzialkaParser(config={}),
    AdresParser(config={}),
    BudynekParser(config={}),
]

PARSERS = {
    parser.FEATURE_TYPE: parser for parser in _parsers_instances
}


def iter_features(gml_path: str):
    """
    Streaming: yields the first child element of each gml:featureMember.
    Structure is like:
    <gml:FeatureCollection gml:id="fc_12345">
        <gml:featureMember>
            <rcn:RCN_Transakcja gml:id="tx_12345">
                ... data ...
            </rcn:RCN_Transakcja>
        </gml:featureMember>
        <gml:featureMember>
            <rcn:RCN_Adres gml:id="ad_67890">
                ... data ...
            </rcn:RCN_Adres>
        </gml:featureMember>
    </gml:FeatureCollection>
    """
    context = ET.iterparse(gml_path, events=("start", "end"))
    _, root = next(context)  # root element for <gml:FeatureCollection .../>

    for event, elem in context:
        if event != "end":
            # still in open tag
            continue

        if local(elem.tag) == "featureMember":
            children = list(elem)
            if children:
                # struct implies that there is exactly one child, which is the actual feature
                yield children[0]

            # important for memory on large files
            elem.clear()
            root.clear()


def count_features(gml_path: str) -> int:
    """
    Count total number of featureMember elements in GML file.
    Coule be `grep`, but we want to avoid external dependencies and be portable across platforms.

    return int(subprocess.run(
        ["grep", "-c", "<gml:featureMember>", gml_path],
        capture_output=True,
        text=True
    ).stdout.strip())
    """
    count = 0
    context = ET.iterparse(gml_path, events=("end",))
    for event, elem in context:
        if local(elem.tag) == "featureMember":
            count += 1
            elem.clear()
    return count


def load_rcn(gml_path: str, db_path: str, batch_size: int = 100000, log_every: int = 500000) -> dict:
    """
    Load RCN GML file into SQLite database.

    Args:
        gml_path: Path to the RCN GML file
        db_path: Path to the SQLite database
        batch_size: Batch size for inserts
        log_every: Log progress every N features

    Returns:
        dict with statistics: processed, inserted, by_type, elapsed
    """
    logger = logging.getLogger("rcn")

    logger.info("=" * 60)
    logger.info("RCN Loader started")
    logger.info("=" * 60)
    logger.info(f"GML file: {gml_path}")
    logger.info(f"Database: {db_path}")
    logger.info(f"Batch size: {batch_size}")
    logger.info(f"Log every N features: {log_every}")

    logger.info("Counting features in GML file...")
    total_features = count_features(gml_path)
    logger.info(f"Total features to process: {total_features}")
    logger.info("=" * 60)

    conn = sqlite3.connect(db_path)

    for p in PARSERS.values():
        p.ensure_schema(conn)
    conn.commit()

    buffers = {ft: [] for ft in PARSERS.keys()}
    processed = 0
    inserted = 0
    inserted_by_type = {}
    seen_by_type = {}

    def flush():
        nonlocal inserted
        batch_inserted = 0
        batch_details = []
        for ft, parser in PARSERS.items():
            buf = buffers[ft]
            if not buf:
                continue
            num_inserted = parser.insert_many(conn, buf)
            batch_inserted += num_inserted
            inserted += num_inserted
            inserted_by_type[ft] = inserted_by_type.get(ft, 0) + num_inserted
            batch_details.append(f"{ft}={num_inserted}")
            buf.clear()
        conn.commit()
        details_str = ", ".join(batch_details)
        logger.info(f"[flush] batch_rows={batch_inserted} ({details_str}), total_inserted={inserted}")

    start = time.time()
    try:
        for feature in iter_features(gml_path):
            processed += 1

            ftype = local(feature.tag)
            seen_by_type[ftype] = seen_by_type.get(ftype, 0) + 1

            p = PARSERS.get(ftype)
            if not p:
                logger.warning(f"unknown feature type: {ftype}")
                continue

            row = p.parse(feature)
            if row is not None:
                buffers[ftype].append(row)

            if any(len(b) >= batch_size for b in buffers.values()):
                flush()

            if log_every and processed % log_every == 0:
                pct = (processed / total_features) * 100
                logger.info(f"[progress] {pct:.1f}% ({processed}/{total_features}), inserted={inserted}")

        flush()

        logger.info("[summary] processed by type:")
        for k in sorted(seen_by_type):
            logger.info(f"  {k}: {seen_by_type[k]}")

        logger.info("[summary] inserted by type:")
        for k in sorted(inserted_by_type):
            logger.info(f"  {k}: {inserted_by_type[k]}")

        elapsed = time.time() - start
        logger.info(f"Done. processed={processed}, inserted={inserted}, db={db_path}, time={elapsed:.0f}s")

        return {
            "processed": processed,
            "inserted": inserted,
            "seen_by_type": seen_by_type,
            "inserted_by_type": inserted_by_type,
            "elapsed": elapsed,
        }
    finally:
        conn.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gml_path", default="../rcn.gml",
                    help="Path to the RCN GML file (default: rcn.gml)")
    ap.add_argument("--db", default="rcn_raw.sqlite",
                    help="Path to the SQLite database (default: rcn_raw.sqlite)")
    ap.add_argument("--batch", type=int, default=100000,
                    help="Batch size for inserts (default: 100000)")
    ap.add_argument("--log-every", type=int, default=500000,
                    help="Print progress every N features (default: 500000)")
    args = ap.parse_args()

    setup_logging()
    load_rcn(args.gml_path, args.db, args.batch, args.log_every)


if __name__ == "__main__":
    main()

