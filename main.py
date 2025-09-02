from merge_csv_data import merge_csv_files
from EdgeList import create_edge_list
from utils import (
    attempt_connection_to_telegram,
    create_network_visualization_guide,
    final_message,
    help,
    intro,
    printC,
    retrieve_api_details,
)
from config import Config
from recommendations import get_channel_recommendations, process_urls

from telethon.errors.rpcerrorlist import ChannelPrivateError
from telethon.tl.types import Channel, User, PeerChannel
from collections import deque
import datetime
import asyncio
import logging
import os
import csv
import time

# Set up logging
logger = logging.getLogger(__name__)


async def process_channels(client, csv_file_path, initial_channels, iterations, min_mentions=5, max_posts=None,
                           include_recommendations=True, recommendations_depth=2, include_urls=True):
    """
    Process channels using snowball sampling technique.

    Args:
        client (TelegramClient): Initialized Telegram client
        csv_file_path (str): Path to the CSV file for results
        initial_channels (list): Initial seed channels
        iterations (int): Number of iterations to perform
        min_mentions (int): Minimum number of mentions to include a channel
        max_posts (int, optional): Maximum number of posts to check per channel
        include_recommendations (bool): Whether to include channel recommendations
        recommendations_depth (int): Maximum depth for recommendations
        include_urls (bool): Whether to extract and process URLs

    Returns:
        tuple: Results, durations, channel counts, and total messages processed
    """
    # Initial variables defined
    processed_channels, channels_to_process = set(), deque(initial_channels)
    processed_channel_ids = set()  # Track processed channels by ID
    iteration_results, iteration_durations, mention_counter = [], [], {}
    total_messages_processed, channel_counts = 0, []

    # Set up URL file if needed
    url_file = None
    if include_urls:
        url_file_path = os.path.join(Config.RESULTS_FOLDER,
                                     f"urls_{datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.txt")
        url_file = open(url_file_path, 'w', encoding='utf-8')
        logger.info(f"URLs will be saved to {url_file_path}")

    for iteration in range(iterations):
        iteration_start_time = time.time()
        current_iteration_channels = set()
        current_iteration_channel_names = {}
        current_iteration_channel_entities = {}  # Store actual channel entities
        iteration_number = iteration + 1  # (adjust for zero indexed value meaning first iter is displayed as 1 & not 0)

        logger.info(f"Starting iteration {iteration_number}/{iterations}")

        while channels_to_process:
            channel = channels_to_process.popleft()

            try:
                # Get the channel entity
                channel_entity = await client.get_entity(channel)
                channel_name = getattr(channel_entity, 'title', 'Unknown')
                channel_username = getattr(channel_entity, 'username', 'Unknown')
                channel_id = getattr(channel_entity, 'id', None)

                # Skip if we couldn't get a valid channel ID
                if channel_id is None:
                    logger.warning(f"Could not get valid ID for channel: {channel}")
                    continue

                # Convert ID to string to ensure consistency
                channel_id_str = str(channel_id)

                if Config.DEBUG:
                    logger.debug(f"Processing channel: {channel_name} (@{channel_username}, ID: {channel_id_str})")

                # Check if we've already processed this channel
                if channel_id not in processed_channel_ids:
                    processed_channels.add(channel)
                    processed_channel_ids.add(channel_id)

                    # Process channel recommendations if enabled
                    if include_recommendations:
                        recommendation_channels = await get_channel_recommendations(
                            client,
                            channel_entity,
                            max_depth=recommendations_depth,
                            edge_list_writer=create_edge_list
                        )
                        # Add recommendations to the channels to process
                        for recommended_channel in recommendation_channels:
                            if recommended_channel not in processed_channels:
                                channels_to_process.append(recommended_channel)

                    # Process URLs if enabled
                    if include_urls:
                        await process_urls(client, channel_entity, create_edge_list, url_file)

                    try:
                        channel_message_count = 0

                        async for message in client.iter_messages(channel):
                            if Config.DEBUG and total_messages_processed % 100 == 0:
                                print(f'Processing message {total_messages_processed}...', end='\r')

                            total_messages_processed += 1

                            if message.forward:
                                # Check if the forward is from a channel
                                fwd_from = message.forward.chat if isinstance(message.forward.chat, Channel) else None

                                if fwd_from:
                                    fwd_from_id = getattr(fwd_from, 'id', None)

                                    # Skip if we couldn't get a valid channel ID
                                    if fwd_from_id is None:
                                        logger.warning(
                                            f"Could not get valid ID for forwarded channel in message {message.id}")
                                        continue

                                    # Convert to string for the counter
                                    fwd_from_id_str = str(fwd_from_id)

                                    mention_counter[fwd_from_id_str] = mention_counter.get(fwd_from_id_str, 0) + 1

                                    if mention_counter[fwd_from_id_str] >= min_mentions:
                                        try:
                                            # Get the forwarding channel's entity, name, and username
                                            fwd_from_entity = await client.get_entity(fwd_from)
                                            fwd_from_name = getattr(fwd_from_entity, 'title', 'Unknown')
                                            fwd_from_username = getattr(fwd_from_entity, 'username', 'Unknown')

                                            # Call the function to create the edge list
                                            create_edge_list(
                                                Config.EDGE_LIST_FOLDER,
                                                Config.EDGE_LIST_FILENAME,
                                                fwd_from_id_str,
                                                fwd_from_name,
                                                fwd_from_username,
                                                channel_id_str,
                                                channel_name,
                                                channel_username,
                                                connection_type="forward"
                                            )

                                            # Write to CSV immediately upon finding a forward
                                            with open(csv_file_path, 'a', newline='', encoding='utf-8') as file:
                                                writer = csv.writer(file)
                                                writer.writerow([fwd_from_id_str, fwd_from_name, fwd_from_username])
                                                file.flush()

                                            # Add to current iteration's channels
                                            current_iteration_channels.add(fwd_from_id)
                                            current_iteration_channel_names[fwd_from_id] = fwd_from_name
                                            current_iteration_channel_entities[fwd_from_id] = fwd_from_entity

                                            # Display progress
                                            queue = len(channels_to_process)
                                            completed = len(processed_channels)

                                            print(
                                                f'Processed messages: [{total_messages_processed}]; channels: [{completed}]'
                                                f' (iteration {iteration_number}/{iterations}) Left in queue: {queue} '
                                                f'¦ Forward found in: {channel} = {channel_name} <<< '
                                                f'{fwd_from_id} = {fwd_from_name} ')

                                        except Exception as ex:
                                            logger.error(f"Error processing forward: {ex}")
                                            if Config.DEBUG:
                                                import traceback
                                                logger.error(traceback.format_exc())

                            channel_message_count += 1
                            if max_posts and channel_message_count >= max_posts:
                                break

                    except ChannelPrivateError:
                        logger.warning(f"Cannot access private channel: {channel}")
                        continue

                    except Exception as ex:
                        logger.error(f"Unexpected error processing channel {channel}: {ex}")
                        if Config.DEBUG:
                            import traceback
                            logger.error(traceback.format_exc())

            except ChannelPrivateError:
                logger.warning(f"Cannot access private channel or banned from channel: {channel}")
                continue

            except Exception as ex:
                logger.error(f"Unexpected error with channel {channel}: {ex}")
                if Config.DEBUG:
                    import traceback
                    logger.error(traceback.format_exc())

        # Store data for this iteration
        iteration_data = [(cid, current_iteration_channel_names[cid]) for cid in current_iteration_channels]
        iteration_results.append(iteration_data)

        # Add new channels to process for next iteration - use actual entities if available
        for new_channel_id in current_iteration_channels:
            if new_channel_id not in processed_channel_ids:
                # Use the entity if we have it, otherwise use the ID with PeerChannel
                if new_channel_id in current_iteration_channel_entities:
                    channels_to_process.append(current_iteration_channel_entities[new_channel_id])
                else:
                    # Try to create a proper PeerChannel object
                    try:
                        channels_to_process.append(PeerChannel(new_channel_id))
                    except:
                        # Fall back to adding just the ID
                        channels_to_process.append(new_channel_id)

        # Calculate and store iteration metrics
        iteration_end_time = time.time()
        iteration_duration = iteration_end_time - iteration_start_time
        iteration_durations.append(iteration_duration)
        channel_counts.append(len(current_iteration_channels))

        logger.info(f"Completed iteration {iteration_number}/{iterations} in {iteration_duration:.2f} seconds")
        logger.info(f"Found {len(current_iteration_channels)} channels in this iteration")

    # Close URL file if it was opened
    if url_file:
        url_file.close()

    return iteration_results, iteration_durations, channel_counts, total_messages_processed


async def main():
    """Main function to execute the snowball sampling process"""
    # Make sure we load the latest env values
    Config.reload_env()

    # Check if API credentials exist before attempting connection
    if not Config.API_ID or not Config.API_HASH:
        logger.warning("No API credentials found in .env file, will prompt user")
        # Get credentials from user input and update config
        api_id, api_hash = retrieve_api_details()
        Config.API_ID = int(api_id) if api_id.isdigit() else api_id
        Config.API_HASH = api_hash
        # Reload config after credentials have been updated
        Config.reload_env()

    # Connect to Telegram
    client = await attempt_connection_to_telegram()

    # Validate configuration after reload
    if not Config.validate():
        logger.error("Configuration validation failed. Please check your .env file.")
        await client.disconnect()
        return

    # Display intro
    intro()

    # Get user input for channels and parameters
    initial_channels_input = input("\nEnter comma-separated Telegram Channel(s) (or type 'help'): ")

    # Run the help function then prompt user if requested
    if initial_channels_input.lower() == "help":
        help()
        initial_channels_input = input("\nEnter Telegram Channel(s): ")

    initial_channels = [channel.strip() for channel in initial_channels_input.split(',') if channel.strip()]

    if not initial_channels:
        logger.error("No valid channels provided. Exiting.")
        await client.disconnect()
        return

    # Get user input for iterations
    iterations_input = input(
        f"\nHow many iterations do you want this to run for ({Config.DEFAULT_ITERATIONS} recommended)? Enter number: ")
    iterations = int(iterations_input) if iterations_input.strip() else Config.DEFAULT_ITERATIONS

    # Get user input for minimum mentions
    min_mentions_input = input(
        f"\nWhat should be the minimum number of times a channel is mentioned to be included ({Config.DEFAULT_MIN_MENTIONS} recommended)? Enter number: ")
    min_mentions = int(min_mentions_input) if min_mentions_input.strip() else Config.DEFAULT_MIN_MENTIONS

    # Get user input for maximum posts
    max_posts_input = input(
        f"\nEnter max number of posts to check per channel (Recommended ~100-1000; leave blank for {'no limit' if Config.DEFAULT_MAX_POSTS is None else Config.DEFAULT_MAX_POSTS}): ")
    max_posts = int(max_posts_input) if max_posts_input.strip() else Config.DEFAULT_MAX_POSTS

    # Ask about channel recommendations
    include_recommendations_input = input(
        f"\nInclude channel recommendations? (y/n, default: {Config.DEFAULT_INCLUDE_RECOMMENDATIONS}): ")
    include_recommendations = Config.DEFAULT_INCLUDE_RECOMMENDATIONS
    if include_recommendations_input.strip().lower() in ('n', 'no', 'false', '0'):
        include_recommendations = False

    # If including recommendations, ask for depth
    recommendations_depth = Config.DEFAULT_RECOMMENDATIONS_DEPTH
    if include_recommendations:
        recommendations_depth_input = input(
            f"\nMaximum depth for channel recommendations ({Config.DEFAULT_RECOMMENDATIONS_DEPTH} recommended)? Enter number: ")
        recommendations_depth = int(
            recommendations_depth_input) if recommendations_depth_input.strip() else Config.DEFAULT_RECOMMENDATIONS_DEPTH

    # Ask about URL extraction
    include_urls_input = input(f"\nExtract URLs from messages? (y/n, default: {Config.DEFAULT_INCLUDE_URLS}): ")
    include_urls = Config.DEFAULT_INCLUDE_URLS
    if include_urls_input.strip().lower() in ('n', 'no', 'false', '0'):
        include_urls = False

    # Record start time
    start_time = time.time()

    try:
        # Writing results to CSV
        datetimestamp = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')

        # Define the directory and filename
        directory = Config.RESULTS_FOLDER
        filename = f'snowball_sampler_results_{datetimestamp}.csv'
        file_path = os.path.join(directory, filename)

        # Create the directory if it does not exist
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Created directory: {directory}")

        # Create CSV with headers
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Channel ID', 'Channel Name', 'Channel Username'])

        logger.info(f"Created output file: {file_path}")

    except IOError as e:
        logger.error(f"IOError occurred: {e}")
        await client.disconnect()
        return

    # Run the snowball sampling process
    try:
        results, iteration_durations, channel_counts, total_messages_processed = await process_channels(
            client,
            file_path,
            initial_channels,
            iterations,
            min_mentions,
            max_posts,
            include_recommendations,
            recommendations_depth,
            include_urls
        )
    except Exception as e:
        logger.error(f"Error during processing: {e}")
        if Config.DEBUG:
            import traceback
            logger.error(traceback.format_exc())
        await client.disconnect()
        return

    # Disconnect from Telegram
    await client.disconnect()

    # Show final results
    final_message(start_time, total_messages_processed, iteration_durations, channel_counts)

    # Create network visualization guide
    create_network_visualization_guide()


if __name__ == '__main__':
    try:
        # Running the main function in an event loop
        asyncio.run(main())

        # Run Merge CSV Script -- retains the output CSV of this run but appends data to merged CSV as well
        print('Collating output files to master list in /merged folder...')
        merge_csv_files(
            Config.RESULTS_FOLDER,
            Config.MERGED_FOLDER,
            Config.MERGED_FILENAME,
            "channels.csv"
        )
        print('Process Complete.')

        # Offer to run network analysis
        run_analysis = input("\nWould you like to run network analysis on the collected data? (y/n): ")
        if run_analysis.strip().lower() in ('y', 'yes', 'true', '1'):
            print("Running network analysis...")
            try:
                import network_analysis
                import sys
                import subprocess

                edge_list_path = os.path.join(Config.EDGE_LIST_FOLDER, Config.EDGE_LIST_FILENAME)
                output_dir = "network_analysis"

                # Make sure the script is executable
                subprocess.run([sys.executable, "network_analysis.py",
                                "--edge-list", edge_list_path,
                                "--output-dir", output_dir])

                print(f"Analysis complete! Results saved to {output_dir} directory.")
            except Exception as e:
                print(f"Error running network analysis: {e}")
                print("You can run it manually with: python network_analysis.py")

    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Saving any collected data...")
    except Exception as e:
        logger.critical(f"Critical error: {e}")
        if Config.DEBUG:
            import traceback

            logger.critical(traceback.format_exc())