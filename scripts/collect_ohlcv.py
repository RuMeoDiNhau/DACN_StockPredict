"""CLI for OHLCV backfill and incremental daily updates."""

import argparse
import logging
import sys
from datetime import date, datetime, timedelta
from typing import Dict, Iterable, List, Optional

from config.settings import Config
from data.collector import DataCollector
from data.database import DatabaseManager
from data.validation import validate_ohlcv


DEFAULT_BACKFILL_DAYS = 1825
DEFAULT_INITIAL_DAYS = 365
OVERLAP_DAYS = 5


def parse_symbols(value: str) -> List[str]:
    """Parse, normalize, and de-duplicate comma-separated symbols."""
    symbols = []
    for item in value.split(","):
        symbol = item.strip().upper().replace(".VN", "")
        if symbol and symbol not in symbols:
            symbols.append(symbol)
    if not symbols:
        raise ValueError("--symbols must contain at least one symbol")
    return symbols


def positive_days(value: str) -> int:
    try:
        days = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("days must be a positive integer") from exc
    if days <= 0:
        raise argparse.ArgumentTypeError("days must be a positive integer")
    return days


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Collect daily OHLCV into SQLite")
    parser.add_argument("--verbose", action="store_true", help="show debug logging")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in ("backfill", "daily-update"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("--symbols", required=True, help="comma-separated symbols")
        subparser.add_argument("--source", default="VCI", help="vnstock source (default: VCI)")
        if command == "backfill":
            subparser.add_argument("--days", type=positive_days, default=DEFAULT_BACKFILL_DAYS)
    return parser


def _date_text(value) -> str:
    return value.strftime("%Y-%m-%d") if hasattr(value, "strftime") else str(value)[:10]


def _collect_one(
    collector: DataCollector,
    database: DatabaseManager,
    symbol: str,
    source: str,
    *,
    days: int,
    start_date: Optional[str] = None,
) -> Dict:
    """Collect one symbol atomically and return rows written."""
    try:
        data = collector.fetch_stock_data(
            symbol, days=days, source=source, start_date=start_date
        )
        if data is None or data.empty:
            raise ValueError("source returned no data")
        valid = validate_ohlcv(data, symbol)
        collector.save_raw_data(valid, symbol)
        rows_written = database.upsert_stock_data(valid)
        database.upsert_ingestion_status(
            symbol,
            source,
            last_success_at=datetime.now().astimezone().isoformat(),
            last_data_date=_date_text(valid["Date"].max()),
            row_count=database.count_stock_rows(symbol),
            last_error=None,
        )
        print(
            f"[OK] {symbol}: fetched={len(valid)}, saved={rows_written}, "
            f"dates={_date_text(valid['Date'].min())}..{_date_text(valid['Date'].max())}"
        )
        return {
            "success": True,
            "fetched": len(valid),
            "saved": rows_written,
            "start": _date_text(valid["Date"].min()),
            "end": _date_text(valid["Date"].max()),
        }
    except Exception as exc:  # one symbol must not stop the batch
        message = str(exc)
        logging.getLogger(__name__).error("[FAIL] %s: %s", symbol, message)
        database.upsert_ingestion_status(symbol, source, last_error=message)
        return {"success": False, "fetched": 0, "saved": 0, "error": message}


def run_backfill(symbols: Iterable[str], days: int, source: str, *, collector=None, database=None) -> int:
    collector = collector or DataCollector()
    database = database or DatabaseManager()
    results = [_collect_one(collector, database, symbol, source, days=days) for symbol in symbols]
    return _summary(results)


def run_daily_update(symbols: Iterable[str], source: str, *, collector=None, database=None) -> int:
    collector = collector or DataCollector()
    database = database or DatabaseManager()
    results = []
    today = date.today()
    for symbol in symbols:
        latest = database.get_latest_stock_date(symbol)
        if latest and latest >= today.isoformat():
            print(f"[SKIP] {symbol}: latest persisted date is {latest}")
            results.append({"success": True, "fetched": 0, "saved": 0, "start": latest, "end": latest})
            continue
        if latest:
            start = datetime.strptime(latest, "%Y-%m-%d").date() - timedelta(days=OVERLAP_DAYS)
            days = max(1, (today - start).days)
            print(f"[INFO] {symbol}: incremental range starts {start.isoformat()} (overlap {OVERLAP_DAYS} days)")
            results.append(_collect_one(collector, database, symbol, source, days=days, start_date=start.isoformat()))
        else:
            print(f"[INFO] {symbol}: no existing data; loading {DEFAULT_INITIAL_DAYS} days")
            results.append(_collect_one(collector, database, symbol, source, days=DEFAULT_INITIAL_DAYS))
    return _summary(results)


def _summary(results: List[Dict]) -> int:
    succeeded = sum(result["success"] for result in results)
    failed = len(results) - succeeded
    fetched = sum(result["fetched"] for result in results)
    saved = sum(result["saved"] for result in results)
    ranges = [(result.get("start"), result.get("end")) for result in results if result.get("start")]
    range_text = "n/a"
    if ranges:
        range_text = f"{min(item[0] for item in ranges)}..{max(item[1] for item in ranges)}"
    print(
        f"Summary: symbols={len(results)}, success={succeeded}, failed={failed}, "
        f"rows_fetched={fetched}, rows_saved={saved}, dates={range_text}"
    )
    return 0 if failed == 0 else 1


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(levelname)s %(message)s")
    try:
        symbols = parse_symbols(args.symbols)
    except ValueError as exc:
        parser.error(str(exc))
    if args.command == "backfill":
        return run_backfill(symbols, args.days, args.source)
    return run_daily_update(symbols, args.source)


if __name__ == "__main__":
    sys.exit(main())
