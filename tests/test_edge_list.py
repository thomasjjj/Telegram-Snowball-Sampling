from __future__ import annotations

import csv
from pathlib import Path

from EdgeList import create_edge_list


def test_create_edge_list_writes_header_and_appends(tmp_path: Path) -> None:
    path = tmp_path / 'edges' / 'edges.csv'
    create_edge_list(
        path,
        from_channel_id=1,
        from_channel_name='A',
        from_channel_username='a',
        to_channel_id=2,
        to_channel_name='B',
        to_channel_username='b',
        connection_type='forward',
        weight=1,
    )
    create_edge_list(
        path,
        from_channel_id=3,
        from_channel_name='C',
        from_channel_username='c',
        to_channel_id=4,
        to_channel_name='D',
        to_channel_username='d',
        connection_type='recommendation',
        weight=2,
    )

    with path.open(newline='', encoding='utf-8') as file:
        reader = list(csv.reader(file))

    assert reader[0] == [
        'From_Channel_ID',
        'From_Channel_Name',
        'From_Channel_Username',
        'To_Channel_ID',
        'To_Channel_Name',
        'To_Channel_Username',
        'ConnectionType',
        'Weight',
    ]
    assert reader[1] == ['1', 'A', 'a', '2', 'B', 'b', 'forward', '1']
    assert reader[2] == ['3', 'C', 'c', '4', 'D', 'd', 'recommendation', '2']
