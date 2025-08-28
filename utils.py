from telethon import TelegramClient
from colorama import Style, Fore
from config import Config

import os
import json
import csv
import re
import time
import logging
import shutil
from typing import Any

# Set up logging
logger = logging.getLogger(__name__)


def intro() -> None:
    """Display the introduction ASCII art and warning messages"""
    printC(r'''
              __________-------____                 ____-------__________
          \------____-------___--__---------__--___-------____------/
           \//////// / / / / / \   _-------_   / \ \ \ \ \ \\\\\\\\/
             \////-/-/------/_/_| /___   ___\ |_\_\------\-\-\\\\/
               --//// / /  /  //|| (O)\ /(O) ||\\  \  \ \ \\\\--
                    ---__/  // /| \_  /V\  _/ |\ \\  \__---
                         -//  / /\_ busting _/\ \  \\- 
                           \_/_/ /\bad guys!/\ \_\_/
                               ----\   |   /----
                                    | -|- |
                                   /   |   \
                                   ---- \___|''', Fore.LIGHTMAGENTA_EX)
    logger.info("                     ===================================")
    logger.info("                     _TELEGRAM CHANNEL SNOWBALL SAMPLER_")
    logger.info("                     Created by Tom Jarvis. Use for good")
    logger.info("                     ===================================\n")

    printC(
        '-- Warning: Due to exponential growth, execution time can be extensive. \n   More than three iterations may take weeks. Apply appropriate filtering.\n'
        '-- Use a sockpuppet account for Telegram research.\n-- Note: Tool lacks content filters. Be aware of potential illegal content.',
        Fore.YELLOW)


def final_message(start_time: float, total_messages_processed: int,
                  iteration_durations: list[float], channel_counts: list[int]) -> None:
    """Display final statistics after completion"""
    end_time = time.time()
    total_time = end_time - start_time

    logger.info("\n==== EXECUTION SUMMARY ====")
    logger.info("Total messages processed: %d", total_messages_processed)

    # Print iteration durations
    for i, duration in enumerate(iteration_durations, 1):
        logger.info("Iteration %d time: %.2f seconds", i, duration)

    # Calculate and print human-readable total time
    hours, remainder = divmod(total_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    time_str = ""
    if hours > 0:
        time_str += f"{int(hours)} hours, "
    if minutes > 0:
        time_str += f"{int(minutes)} minutes, "
    time_str += f"{seconds:.2f} seconds"

    logger.info("Total execution time: %s", time_str)

    # Print the number of channels per iteration
    logger.info("\n==== CHANNELS PER ITERATION ====")
    for i, count in enumerate(channel_counts, 1):
        logger.info("Number of channels in iteration %d: %d", i, count)

    # Total channels
    total_channels = sum(channel_counts)
    logger.info("Total unique channels discovered: %d", total_channels)

    # Suggest network analysis
    logger.info("\n==== NEXT STEPS ====")
    logger.info("Your edge list has been saved to the EdgeList folder.")
    logger.info("For network visualization, you can import Edge_List.csv into Gephi or similar software.")
    logger.info("For detailed analysis, examine the URLs collected in the results folder.")


def split_search_terms(input_string: str) -> list[str]:
    """Split a comma-separated string into a list of terms"""
    return [term.strip() for term in input_string.split(',')]


def sanitize_filename(filename: str) -> str:
    """Sanitize the filename by removing or replacing characters that may cause issues"""
    return re.sub(r'[<>:"/\\|?*]', '', filename)


def printC(string: str, colour: str, level: int = logging.INFO) -> None:
    """Log colored text.

    Args:
        string (str): The text to log
        colour (str): Color from colorama.Fore
        level (int, optional): Logging level. Defaults to logging.INFO.
    """
    logger.log(level, "%s%s%s", colour, string, Style.RESET_ALL)


def remove_inaccessible_channels(file_path: str, inaccessible_channels: list[str]) -> None:
    """Remove inaccessible channels from a CSV file.

    Args:
        file_path (str): Path to the CSV file
        inaccessible_channels (list[str]): List of channel names to remove
    """
    logger.info(
        "Removing %d inaccessible channels from %s",
        len(inaccessible_channels),
        file_path,
    )

    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            fieldnames = reader.fieldnames
            channels = [row for row in reader if row['Channel Name'] not in inaccessible_channels]

        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(channels)

        logger.info("Successfully removed inaccessible channels from %s", file_path)
    except Exception as e:
        logger.error("Error removing inaccessible channels: %s", e)


def write_to_text_file(data: Any, filename: str) -> None:
    """Write data to a text file as JSON (backup mechanism).

    Args:
        data (Any): Data to write to the file
        filename (str): Path to the output file
    """
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)
        logger.info("Data written to %s", filename)
    except Exception as e:
        logger.error("Failed to write to text file: %s", e)


async def attempt_connection_to_telegram() -> TelegramClient:
    """Connect to Telegram API using credentials from config or by prompting the user.

    Returns:
        TelegramClient: A connected TelegramClient instance
    """
    # Try to get API details from environment first
    api_id = Config.API_ID
    api_hash = Config.API_HASH

    # If not in environment, try to get from file or prompt user
    if not api_id or not api_hash:
        api_id, api_hash = retrieve_api_details()

    # Create and start the client
    client = TelegramClient(Config.SESSION_NAME, int(api_id), api_hash)
    await client.start()

    logger.info("Connection to Telegram established.")
    logger.info("Please wait...")
    return client


def retrieve_api_details() -> tuple[str, str]:
    """Retrieve API details from .env file or prompt user and create .env file.

    Returns:
        tuple[str, str]: API ID and API Hash
    """
    # Check if .env file exists
    env_file_path = '.env'
    example_env_path = 'example.env'

    if not os.path.exists(env_file_path):
        # No .env file, check if example.env exists
        if os.path.exists(example_env_path):
            logger.info("Creating .env file from example.env template")
            # Copy example.env to .env
            shutil.copy2(example_env_path, env_file_path)
        else:
            # Create a basic .env file
            logger.info("Creating new .env file")
            with open(env_file_path, 'w', encoding='utf-8') as f:
                f.write("""# Telegram API credentials
TELEGRAM_API_ID=
TELEGRAM_API_HASH=
TELEGRAM_SESSION_NAME=session_name

# Snowball sampling configuration
DEFAULT_MIN_MENTIONS=5
DEFAULT_ITERATIONS=3
DEFAULT_MAX_POSTS=100

# Channel recommendations configuration
DEFAULT_INCLUDE_RECOMMENDATIONS=True
DEFAULT_RECOMMENDATIONS_DEPTH=2

# URL extraction configuration
DEFAULT_INCLUDE_URLS=True

# File paths and directories
RESULTS_FOLDER=results
MERGED_FOLDER=merged
EDGE_LIST_FOLDER=EdgeList
EDGE_LIST_FILENAME=Edge_List.csv
MERGED_FILENAME=merged_channels.csv
API_DETAILS_FILE=api_values.txt

# Debug mode
DEBUG=False
""")

    # Prompt user for API credentials
    logger.info(
        '\nPlease enter your Telegram API credentials\n'
        'These can be retrieved from https://my.telegram.org/auth\n'
    )
    api_id = input("Enter your API ID: ").strip()
    api_hash = input("Enter your API Hash: ").strip()

    # Update the .env file with the provided credentials
    update_env_file(env_file_path, api_id, api_hash)

    # Log the retrieval
    logger.info("API ID retrieved and saved to .env: %s", api_id)
    logger.info(
        "\nAPI ID saved: %s ¦ API Hash saved: %s...%s\n",
        api_id,
        api_hash[0:3],
        api_hash[-3:],
    )

    return api_id, api_hash


def update_env_file(env_file_path: str, api_id: str, api_hash: str) -> None:
    """Update the .env file with new API credentials.

    Args:
        env_file_path (str): Path to the .env file
        api_id (str): The API ID
        api_hash (str): The API Hash
    """
    try:
        # Read the current .env file
        with open(env_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Update the API credentials in the file
        updated_lines = []
        for line in lines:
            if line.startswith('TELEGRAM_API_ID='):
                updated_lines.append(f'TELEGRAM_API_ID={api_id}\n')
            elif line.startswith('TELEGRAM_API_HASH='):
                updated_lines.append(f'TELEGRAM_API_HASH={api_hash}\n')
            else:
                updated_lines.append(line)

        # Write the updated content back to the file
        with open(env_file_path, 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)

        logger.info("Successfully updated API credentials in .env file")
    except Exception as e:
        logger.error("Error updating .env file: %s", e)
        # In case of error, write to the file more directly
        try:
            with open(env_file_path, 'w', encoding='utf-8') as f:
                f.write(f"TELEGRAM_API_ID={api_id}\n")
                f.write(f"TELEGRAM_API_HASH={api_hash}\n")
                f.write("TELEGRAM_SESSION_NAME=session_name\n")
                f.write("DEFAULT_MIN_MENTIONS=5\n")
                f.write("DEFAULT_ITERATIONS=3\n")
                f.write("DEFAULT_MAX_POSTS=100\n")
                f.write("DEFAULT_INCLUDE_RECOMMENDATIONS=True\n")
                f.write("DEFAULT_RECOMMENDATIONS_DEPTH=2\n")
                f.write("DEFAULT_INCLUDE_URLS=True\n")
                f.write("RESULTS_FOLDER=results\n")
                f.write("MERGED_FOLDER=merged\n")
                f.write("EDGE_LIST_FOLDER=EdgeList\n")
                f.write("EDGE_LIST_FILENAME=Edge_List.csv\n")
                f.write("MERGED_FILENAME=merged_channels.csv\n")
                f.write("DEBUG=False\n")
            logger.info("Created new .env file with API credentials")
        except Exception as inner_e:
            logger.error("Failed to create .env file: %s", inner_e)


def help() -> None:
    """Display help information about the tool"""
    printC('''----
    HELP
    ----

    This tool is designed for snowball sampling on Telegram. It has three main discovery methods:

    1. FORWARDED MESSAGES - It takes a "seed" channel and searches it for forwarded
       messages. These forwarded messages come from other channels which are likely 
       to be relevant to the topics of the seed channel.

    2. CHANNEL RECOMMENDATIONS - It fetches the "Recommended Channels" that Telegram
       generates for each channel, discovering related channels.

    3. URL EXTRACTION - It extracts URLs from messages, which can reveal connections
       to external resources.

    --- The number of times the process repeats for forwards is based on the iterations setting.
        Setting it to 3 iterations is usually enough as it is a rapid exponential growth of channels.

    --- Setting the minimum number of mentions helps reduce the number of channels collected and only
        allows the most relevant channels which are frequently forwarded to be added to the list.

    --- For recommendations, you can set a different depth to control how many levels of recommendations
        to follow.

    --- You can enable/disable recommendations and URL extraction to focus on specific types of connections.

    --- Limiting the maximum posts per channel can significantly reduce processing time for large channels.

    Configuration options can be set in the .env file to customize default behavior.''', Fore.GREEN)


def error_fix(results: Any) -> None:
    """Create a backup of results in case of critical error

    Args:
        results (Any): The data to save
    """
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    backup_filename = f'backup_results_{timestamp}.txt'

    printC("Attempting to recover results to text file due to critical issue...", Fore.YELLOW)
    write_to_text_file(results, backup_filename)
    printC(f"Backup saved to {backup_filename}", Fore.GREEN)


def create_network_visualization_guide() -> None:
    """Create a text file with instructions for visualizing the network data"""
    guide_path = os.path.join(Config.RESULTS_FOLDER, "network_visualization_guide.txt")

    guide_content = """
NETWORK VISUALIZATION GUIDE
===========================

The Telegram Snowball Sampling Tool creates network data that can be visualized using specialized software.
This guide will help you visualize the network using Gephi, a popular open-source network visualization tool.

Files to Use
-----------
- Edge_List.csv: Located in the EdgeList folder, contains the connections between channels.

Basic Steps
-----------
1. Download and install Gephi from https://gephi.org/

2. Load the Data:
   - Open Gephi and create a new project
   - Go to File > Import Spreadsheet and select your Edge_List.csv file
   - Import as "Edges table"
   - Make sure "From_Channel_ID" is set as Source and "To_Channel_ID" is set as Target
   - Set "ConnectionType" as Type (if available)
   - Set "Weight" as Weight (if available)
   - Click "Next" and then "Finish"

3. Apply a Layout:
   - Go to the Layout panel (right side)
   - Select "ForceAtlas 2" for a good starting layout
   - Click "Run" and let it organize the nodes
   - Click "Stop" when the layout stabilizes

4. Style the Visualization:
   - In the Appearance panel, you can color nodes based on attributes
   - Size nodes based on "Degree" (number of connections) in the Appearance panel
   - Use the Preview panel to adjust the final look

5. Explore the Network:
   - Use the Filter panel to isolate parts of the network
   - Use the Statistics panel to calculate metrics like centrality
   - Zoom and pan to focus on interesting clusters

Advanced Analysis
----------------
- Community Detection: 
  Run Modularity in the Statistics panel to detect communities

- Key Influencers:
  Calculate Betweenness Centrality to find nodes that act as bridges

- Connection Patterns:
  Look at the distribution of connection types (forwarded messages vs. recommendations)

Exporting Results
----------------
- Use the Preview panel to export as PDF or SVG
- Use the Data Laboratory to export node and edge data for further analysis

For help with Gephi, visit: https://gephi.org/users/

"""

    try:
        with open(guide_path, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        logger.info(f"Network visualization guide created at {guide_path}")
    except Exception as e:
        logger.error(f"Error creating network visualization guide: {e}")