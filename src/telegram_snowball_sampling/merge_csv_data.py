import csv
import logging
from pathlib import Path
from typing import Iterable, List, Sequence, Set, Tuple

logger = logging.getLogger(__name__)

_HEADER: Sequence[str] = ["Channel ID", "Channel Name", "Channel Username"]


def _load_existing_records(path: Path) -> Tuple[List[List[str]], Set[Tuple[str, ...]]]:
    """Load existing rows from the merged CSV if it exists."""

    records: List[List[str]] = []
    seen: Set[Tuple[str, ...]] = set()

    if not path.exists():
        return records, seen

    with path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader, None)  # Skip header
        for row in reader:
            if row:
                record = tuple(row)
                if record not in seen:
                    seen.add(record)
                    records.append(list(record))

    return records, seen


def _iter_new_rows(results_dir: Path) -> Iterable[List[str]]:
    """Yield rows from all CSV files in the results directory."""

    if not results_dir.exists():
        logger.warning("Results directory %s does not exist", results_dir)
        return

    for csv_path in sorted(results_dir.glob("*.csv")):
        with csv_path.open("r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader, None)  # Skip header
            for row in reader:
                if row:
                    yield row


def merge_csv_files(results_folder: str, merged_folder: str, merged_filename: str) -> None:
    """Merge CSV files from the results directory into a deduplicated CSV."""

    logger.info("Merging and de-duplicating CSVs...")

    merged_dir = Path(merged_folder)
    merged_dir.mkdir(parents=True, exist_ok=True)
    merged_path = merged_dir / merged_filename

    records, seen = _load_existing_records(merged_path)

    new_rows = list(_iter_new_rows(Path(results_folder)))
    for row in new_rows:
        record = tuple(row)
        if record not in seen:
            seen.add(record)
            records.append(list(row))

    with merged_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(_HEADER)
        writer.writerows(records)

    logger.info("Merged data written to %s", merged_path)


if __name__ == "__main__":
    merge_csv_files("results", "merged", "merged_channels.csv")
