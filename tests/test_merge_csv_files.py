from __future__ import annotations

import csv
from pathlib import Path

from merge_csv_data import merge_csv_files


def write_csv(path: Path, rows: list[list[str]]) -> None:
    with path.open('w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Channel ID', 'Channel Name', 'Channel Username'])
        writer.writerows(rows)


def test_merge_csv_files_deduplicates(tmp_path: Path) -> None:
    results_dir = tmp_path / 'results'
    merged_dir = tmp_path / 'merged'
    results_dir.mkdir()
    merged_dir.mkdir()

    write_csv(
        results_dir / 'file1.csv',
        [['1', 'ChannelA', 'usera'], ['2', 'ChannelB', 'userb']],
    )
    write_csv(
        results_dir / 'file2.csv',
        [['2', 'ChannelB', 'userb'], ['3', 'ChannelC', 'userc']],
    )

    merge_csv_files(
        str(results_dir),
        str(merged_dir),
        'merged_channels.csv',
    )

    with (merged_dir / 'merged_channels.csv').open(newline='', encoding='utf-8') as file:
        reader = list(csv.reader(file))

    assert reader[0] == ['Channel ID', 'Channel Name', 'Channel Username']
    assert sorted(reader[1:]) == [
        ['1', 'ChannelA', 'usera'],
        ['2', 'ChannelB', 'userb'],
        ['3', 'ChannelC', 'userc'],
    ]
