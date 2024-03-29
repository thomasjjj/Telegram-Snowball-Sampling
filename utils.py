from telethon import TelegramClient
from colorama import Style, Fore  # import Style, Fore << both must be included even if Fore is removed by your IDE
import os
import json
import csv
import re
import time



def intro():
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
    print("                     ===================================")
    print("                     _TELEGRAM CHANNEL SNOWBALL SAMPLER_")
    print("                     Created by Tom Jarvis. Use for good")
    print("                     ===================================\n")

    printC(
        '-- Warning: Due to exponential growth, execution time can be extensive. \n   More than three iterations may take weeks. Apply appropriate filtering.\n'
        '-- Use a sockpuppet account for Telegram research.\n-- Note: Tool lacks content filters. Be aware of potential illegal content.',
        Fore.YELLOW)

def final_message(start_time, total_messages_processed, iteration_durations, channel_counts):
    end_time = time.time()
    total_time = end_time - start_time
    print(f'Total messages processed: {total_messages_processed}')
    # Print iteration durations
    for i, duration in enumerate(iteration_durations, 1):
        print(f"Iteration {i} time: {duration:.2f} seconds")
    print(f"Total execution time: {total_time} seconds")

    # Print the number of channels per iteration
    for i, count in enumerate(channel_counts, 1):
        print(f"Number of channels in iteration {i}: {count}")

def split_search_terms(input_string):
    return [term.strip() for term in input_string.split(',')]

def sanitize_filename(filename):
    """Sanitize the filename by removing or replacing characters that may cause issues."""
    return re.sub(r'[<>:"/\\|?*]', '', filename)

def printC(string, colour):
    '''Print coloured and then reset: The "colour" variable should be written as "Fore.GREEN" (or other colour) as it
    uses Fore function from colorama. If issues, make sure Fore is imported:

    from colorama import Style, Fore'''

    print(colour + string + Style.RESET_ALL)

def remove_inaccessible_channels(file_path, inaccessible_channels):
    print('Removing inaccessible channels from indexes...', end='\r')
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        channels = [row for row in reader if row['Channel Name'] not in inaccessible_channels]

    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(channels)
    print('Removed inaccessible channels from indexes.')

def write_to_text_file(data, filename):  # In case of emergency and CSV writer doenst work, this dumps output to txt
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Failed to write to text file: {e}")

async def attempt_connection_to_telegram():
    """
        Connects to the Telegram API using the API ID and API hash values stored in a file named 'api_values.txt'.
        If the file does not exist, it prompts the user to enter their API ID and API hash and creates the file.
        ---------------
        Usage:
        client = connect_to_telegram()

        Returns:
            TelegramClient: A connected TelegramClient instance.

        Raises:
            SystemExit: If the connection to the Telegram client fails.
        """

    def retrieve_api_details():
        """
        Retrieve the API details required for TelegramClient from a file,
        or ask the user for them if they're not available.

        Returns:
            tuple: API ID and API Hash as a tuple (api_id, api_hash)
        """

        api_details_file_path = 'api_values.txt'

        # Inner function to warn the user and prompt for API details
        def print_warning_and_prompt():
            nonlocal api_id, api_hash  # Modify variables in the nearest enclosing scope
            print(
                '\nWARNING: No valid API details found.\n'
                'Please enter your API details.\n'
                'API details can be retrieved from https://my.telegram.org/auth\n'
                '\033[0m'
            )
            api_id = input("Enter your API ID: ")
            api_hash = input("Enter your API Hash: ")
            update_file(api_id, api_hash)

        # Inner function to update the file with API details
        def update_file(api_id, api_hash):
            with open(api_details_file_path, 'w') as file:
                file.write(f'api_id:\n{api_id}\n')
                file.write(f'api_hash:\n{api_hash}')

        # Initialise default values
        api_id, api_hash = 0, 'xxxxxxxxxxxxxxxxxxxxxx'

        # Check if file exists
        if os.path.exists(api_details_file_path):
            with open(api_details_file_path, 'r') as file:
                lines = file.readlines()
                # Ensure the file contains the expected number of lines
                if len(lines) >= 4:
                    try:
                        api_id = int(lines[1].strip())
                        api_hash = lines[3].strip()
                    except (ValueError, IndexError):
                        print_warning_and_prompt()
                else:
                    print_warning_and_prompt()
        else:
            print_warning_and_prompt()

        print(f'\nAPI ID retrieved: {api_id} ¦ API Hash retrieved: {api_hash}\n')

        return int(api_id), api_hash

    api_id, api_hash = retrieve_api_details()
    client = TelegramClient('session_name', api_id, api_hash)
    await client.start()

    print("Connection to Telegram established.")
    print("Please wait...")
    return client

def help():
    printC('''----
    HELP
    ----

    This tool is designed for snowball sampling. It takes a "seed" channel and searches it for forwarded
    messages. These forwarded messages come from other channels which are likely to be relevant to the
    topics of the seed channel.

    So we scrape a list of channels in the first instance then we go through those channels and scrape them.
    This means all of the forwards in those channels are also collected, and the process repeats.

    --- The number of times the process repeats is based on the number of iterations you set. 
        Setting it to 3 iterations is usually enough as it is a rapid exponential growth of channels.

    --- Setting the minimum number of mentions helps reduce the number of channels collected and only
        allows the most relevant channels which are frequently forwarded to be added to the list.''', Fore.GREEN)

def error_fix(results):
    # Dumping the data into a text file in case of an error
    printC("Attempting to recover results to text file due to critical issue ...", Fore.YELLOW)
    write_to_text_file(results, 'backup_results.txt')