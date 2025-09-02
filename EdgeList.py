import os
import csv
import logging
from config import Config

# Set up logging
logger = logging.getLogger(__name__)


def create_edge_list(folder_name=None, file_name=None, from_channel_id=None, from_channel_name=None,
                     from_channel_username=None, to_channel_id=None, to_channel_name=None, to_channel_username=None,
                     connection_type="forward", weight=1):
    """
    Create or append to an edge list CSV file to track channel relationships.

    Args:
        folder_name (str, optional): The name of the folder. Default from Config.
        file_name (str, optional): The name of the output file. Default from Config.
        from_channel_id: ID of the source channel
        from_channel_name: Name of the source channel
        from_channel_username: Username of the source channel
        to_channel_id: ID of the target channel or URL
        to_channel_name: Name of the target channel or URL type
        to_channel_username: Username of the target channel or None for URLs
        connection_type (str): Type of connection ("forward", "recommendation", "outbound_link")
        weight (int): Weight of the edge (number of occurrences)
    """
    # Use defaults from Config if parameters are not provided
    folder_name = folder_name or Config.EDGE_LIST_FOLDER
    file_name = file_name or Config.EDGE_LIST_FILENAME

    # Check if parameters are valid
    if from_channel_id is None or to_channel_id is None:
        logger.error(f"Missing required channel IDs for edge list: from_id={from_channel_id}, to_id={to_channel_id}")
        return

    # Convert IDs to strings to avoid type issues
    from_channel_id = str(from_channel_id)
    to_channel_id = str(to_channel_id)

    # Provide default values for missing parameters
    from_channel_name = from_channel_name or 'Unknown'
    from_channel_username = from_channel_username or 'Unknown'
    to_channel_name = to_channel_name or 'Unknown'
    to_channel_username = to_channel_username or 'Unknown'

    try:
        # Check if the folder exists, if not, create it
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
            logger.info(f"Created edge list directory: {folder_name}")

        file_path = os.path.join(folder_name, file_name)

        # Check if file exists, if not, create it with headers
        if not os.path.exists(file_path):
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    'From_Channel_ID', 'From_Channel_Name', 'From_Channel_Username',
                    'To_Channel_ID', 'To_Channel_Name', 'To_Channel_Username',
                    'ConnectionType', 'Weight'
                ])
            logger.info(f"Created edge list file: {file_path}")

        # Append to the file for the current edge
        with open(file_path, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                from_channel_id,
                from_channel_name,
                from_channel_username,
                to_channel_id,
                to_channel_name,
                to_channel_username,
                connection_type,
                weight
            ])

        if Config.DEBUG:
            logger.debug(f"Added edge: {from_channel_name} -> {to_channel_name} ({connection_type})")

    except Exception as e:
        logger.error(f"Error creating edge list entry: {e}")
        if Config.DEBUG:
            import traceback
            logger.error(traceback.format_exc())
