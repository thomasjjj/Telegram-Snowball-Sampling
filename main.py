from merge_csv_data import merge_csv_files
from EdgeList import create_edge_list
from utils import *

from telethon.errors.rpcerrorlist import ChannelPrivateError
from telethon.tl.types import Channel
from collections import deque
import datetime
import asyncio



async def process_channels(client, csv_file_path, initial_channels, iterations, min_mentions=5, max_posts=None):

    # initial variables defined
    processed_channels, channels_to_process = set(), deque(initial_channels)
    iteration_results, iteration_durations, mention_counter, total_messages_processed, channel_counts = [], [], {}, 0, []

    for iteration in range(iterations):
        iteration_start_time = time.time()
        current_iteration_channels = set()
        current_iteration_channel_names = {}
        iteration_number = iteration + 1  # (adjust for zero indexed value meaning first iter is displayed as 1 & not 0)

        while channels_to_process:
            channel = channels_to_process.popleft()

            try:
                channel_entity = await client.get_entity(channel)  # Fetch channel entity and get the channel name
                channel_name = channel_entity.title

                if channel not in processed_channels:
                    processed_channels.add(channel)

                    try:
                        channel_message_count = 0

                        async for message in client.iter_messages(channel):
                            print('Processing message...', end='\r')
                            total_messages_processed += 1
                            fwd_from_name = 'Unknown'  # Initialize with a default value
                            if message.forward:
                                fwd_from = message.forward.chat if isinstance(message.forward.chat, Channel) else None
                                if fwd_from:
                                    mention_counter[fwd_from.id] = mention_counter.get(fwd_from.id, 0) + 1
                                    if mention_counter[fwd_from.id] >= min_mentions:
                                        # Write to CSV immediately upon finding a forward
                                        try:
                                            # Get the forwarding channel's entity, name, and username
                                            fwd_from_entity = await client.get_entity(fwd_from.id)
                                            fwd_from_name = fwd_from_entity.title if fwd_from_entity else 'Unknown'
                                            fwd_from_username = fwd_from_entity.username if fwd_from_entity and hasattr(
                                                fwd_from_entity, 'username') else 'Unknown'

                                            # Get the current channel's entity, name, and username
                                            channel_entity = await client.get_entity(channel)
                                            channel_name = channel_entity.title if channel_entity else 'Unknown'
                                            channel_username = channel_entity.username if channel_entity and hasattr(
                                                channel_entity, 'username') else 'Unknown'

                                            # Call the function to create the edge list
                                            create_edge_list('EdgeList', 'Edge_List.csv', fwd_from.id, fwd_from_name,
                                                             fwd_from_username, channel_entity.id, channel_name,
                                                             channel_username)

                                            # Write to CSV immediately upon finding a forward
                                            with open(csv_file_path, 'a', newline='', encoding='utf-8') as file:
                                                writer = csv.writer(file)
                                                writer.writerow([fwd_from.id, fwd_from_name, fwd_from_username])
                                                file.flush()

                                        except Exception as ex:
                                            printC(f"An error occurred: {ex}", Fore.RED)

                                        current_iteration_channels.add(fwd_from.id)
                                        current_iteration_channel_names[fwd_from.id] = fwd_from_name
                                        queue = len(channels_to_process)
                                        completed = len(processed_channels)

                                        print(f'Processed messages: [{total_messages_processed}]; channels: [{completed}]'
                                              f' (iteration {iteration_number}/{iterations}) Left in queue: {queue} '
                                              f'¦ Forward found in: {channel} = {channel_name} <<< '
                                              f'{fwd_from.id} = {fwd_from_name} ')

                            channel_message_count += 1
                            if max_posts and channel_message_count >= max_posts:
                                break

                    except ChannelPrivateError:
                        printC(f"Cannot access private channel: {channel}", Fore.RED)
                        continue  # Skip further processing of this channel and continue with the next one

                    except Exception as ex:
                        printC(f"An unexpected error occurred while processing channel {channel}: {ex}", Fore.RED)
            except ChannelPrivateError:
                printC(f"Cannot access private channel or banned from channel: {channel}", Fore.RED)
                continue  # Skip further processing of this channel and move to the next one

            except Exception as ex:
                printC(f"An unexpected error occurred while processing channel {channel}: {ex}", Fore.RED)

        iteration_data = [(cid, current_iteration_channel_names[cid]) for cid in current_iteration_channels]
        iteration_results.append(iteration_data)

        for new_channel in current_iteration_channels:
            if new_channel not in processed_channels:
                channels_to_process.append(new_channel)

        iteration_end_time = time.time()
        iteration_duration = iteration_end_time - iteration_start_time
        iteration_durations.append(iteration_duration)

        # Store the number of channels for this iteration
        channel_counts.append(len(current_iteration_channels))

    return iteration_results, iteration_durations, channel_counts, total_messages_processed


async def main():

    intro()
    client = await attempt_connection_to_telegram()

    initial_channels_input = input("\nEnter comma-separated Telegram Channel(s) (or type 'help'): ")

    # run the help function then prompt user
    if initial_channels_input == "help":
        help()
        initial_channels_input = input("\nEnter Telegram Channel(s): ")

    initial_channels = [channel.strip() for channel in initial_channels_input.split(',') if channel.strip()]

    iterations = int(input("\nHow many iterations do you want this to run for (3 recommended)? Enter number: "))
    min_mentions = int(input("\nWhat should be the minimum number of times a channel is mentioned to be included" 
                             " (5 recommended)? Enter number: "))

    max_posts_input = input("\nEnter max number of posts to check per channel (Recommended ~100-1000; leave blank for no limit): ")
    max_posts = int(max_posts_input) if max_posts_input.strip() else None

    start_time = time.time()


    try:
        # Writing results to CSV
        datetimestamp = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')

        # Define the directory and filename
        directory = 'results'
        filename = f'snowball_sampler_results_{datetimestamp}.csv'
        file_path = os.path.join(directory, filename)

        # Create the directory if it does not exist
        if not os.path.exists(directory):
            os.makedirs(directory)

    except IOError as e:
        printC(f"IOError occurred: {e}", Fore.RED)


    results, iteration_durations, channel_counts, total_messages_processed = await process_channels(client, file_path, initial_channels, iterations, min_mentions, max_posts)
    await client.disconnect()


    final_message(start_time, total_messages_processed, iteration_durations, channel_counts)



if __name__ == '__main__':
    # Running the main function in an event loop
    asyncio.run(main())

    # Run Merge CSV Script -- retains the output CSV of this run but appends data to merged CSV as well    print('Collating output files to master list in /merged folder...')
    results_folder, merged_folder, merged_filename = 'results', 'merged', 'merged_channels.csv'
    merge_csv_files(results_folder, merged_folder, merged_filename, "channels.csv")  # Call the function
    print('Process Complete.')
