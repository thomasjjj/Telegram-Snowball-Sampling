import csv
import logging
from pathlib import Path
from typing import TextIO, Union

from config import Config

# Set up logging
logger = logging.getLogger(__name__)


def create_edge_list(
    writer_or_path: Union[csv.writer, TextIO, str, Path],
    from_channel_id: str,
    from_channel_name: str,
    from_channel_username: str,
    to_channel_id: str,
    to_channel_name: str,
    to_channel_username: str | None,
    connection_type: str = "forward",
    weight: int = 1,
) -> None:
    """Write a channel relationship to an edge list CSV file.

    Args:
        writer_or_path: CSV writer, open file handle, or path to the edge list file.
        from_channel_id: ID of the source channel.
        from_channel_name: Name of the source channel.
        from_channel_username: Username of the source channel.
        to_channel_id: ID of the target channel or URL.
        to_channel_name: Name of the target channel or URL type.
        to_channel_username: Username of the target channel or ``None`` for URLs.
        connection_type: Type of connection ("forward", "recommendation", "outbound_link").
        weight: Weight of the edge (number of occurrences).
    """
    # Provide default values for missing parameters
    from_channel_name = from_channel_name or "Unknown"
    from_channel_username = from_channel_username or "Unknown"
    to_channel_name = to_channel_name or "Unknown"
    to_channel_username = to_channel_username or "Unknown"

    try:
        if isinstance(writer_or_path, (str, Path)):
            path = Path(writer_or_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            write_header = not path.exists() or path.stat().st_size == 0
            with path.open("a", newline="", encoding="utf-8") as file:
                csv_writer = csv.writer(file)
                if write_header:
                    csv_writer.writerow([
                        "From_Channel_ID",
                        "From_Channel_Name",
                        "From_Channel_Username",
                        "To_Channel_ID",
                        "To_Channel_Name",
                        "To_Channel_Username",
                        "ConnectionType",
                        "Weight",
                    ])
                csv_writer.writerow([
                    str(from_channel_id),
                    from_channel_name,
                    from_channel_username,
                    str(to_channel_id),
                    to_channel_name,
                    to_channel_username,
                    connection_type,
                    weight,
                ])
        else:
            csv_writer = (
                writer_or_path
                if hasattr(writer_or_path, "writerow")
                else csv.writer(writer_or_path)
            )
            csv_writer.writerow([
                str(from_channel_id),
                from_channel_name,
                from_channel_username,
                str(to_channel_id),
                to_channel_name,
                to_channel_username,
                connection_type,
                weight,
            ])
        if Config.DEBUG:
            logger.debug(
                f"Added edge: {from_channel_name} -> {to_channel_name} ({connection_type})"
            )
    except Exception as e:
        logger.error(f"Error creating edge list entry: {e}")
        if Config.DEBUG:
            import traceback

            logger.error(traceback.format_exc())
