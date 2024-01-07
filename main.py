from telethon.tl.types import Channel
from telethon.errors.rpcerrorlist import ChannelPrivateError
from collections import deque
import asyncio
import csv
import time
from utils import *

async def process_channels(client, initial_channels, iterations, min_mentions=5, max_posts=None):

    # initial variables defined
    processed_channels, channels_to_process = set(), deque(initial_channels)
    iteration_results, mention_counter, total_messages_processed = [], {}, 0

    for iteration in range(iterations):
        current_iteration_channels = set()
        current_iteration_channel_names = {}
        iteration_number = iteration + 1  # (adjust for zero indexed value meaning first iter is displayed as 1 & not 0)

        while channels_to_process:
            channel = channels_to_process.popleft()
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
                                if mention_counter[fwd_from.id] >= min_mentions and fwd_from.id not in processed_channels:
                                    try:
                                        fwd_from_entity = await client.get_entity(fwd_from.id)
                                        fwd_from_name = fwd_from_entity.title if fwd_from_entity else 'Unknown'
                                    except ChannelPrivateError:
                                        printC(f"Cannot access private channel: {fwd_from.id}", Fore.RED)
                                        fwd_from_name = 'Private Channel'
                                    except Exception as ex:
                                        printC(f"An unexpected error occurred: {ex}", Fore.RED)

                                    current_iteration_channels.add(fwd_from.id)
                                    current_iteration_channel_names[fwd_from.id] = fwd_from_name
                                    queue = len(channels_to_process)
                                    completed = len(processed_channels)

                                    print(f'Processed messages: [{total_messages_processed}]; channels: [{completed}] '
                                          f'¦ Forward found from: {channel} - {channel_name} ¦ (iteration'
                                          f' {iteration_number}/{iterations}) ¦ Left in queue: {queue} ¦ '
                                          f'{fwd_from.id} - {fwd_from_name} ')

                        channel_message_count += 1
                        if max_posts and channel_message_count >= max_posts:
                            break

                except ChannelPrivateError:
                    print(f"Cannot access private channel: {channel}")
                except Exception as ex:
                    print(f"An unexpected error occurred while processing channel {channel}: {ex}")

        iteration_data = [(cid, current_iteration_channel_names[cid]) for cid in current_iteration_channels]
        iteration_results.append(iteration_data)

        for new_channel in current_iteration_channels:
            if new_channel not in processed_channels:
                channels_to_process.append(new_channel)

    return iteration_results


async def main():

    intro()
    client = await attempt_connection_to_telegram()

    initial_channels_input = input("\nEnter comma-separated Telegram Channel(s) (or type 'help'): ")

    # run the help function then prompt user
    if initial_channels_input == "help":
        help()
        initial_channels_input = input("\nEnter Telegram Channel(s): ")

    initial_channels = [channel.strip() for channel in initial_channels_input.split(',') if channel.strip()]

    iterations = int(input("How many iterations do you want this to run for (3 recommended)? Enter number: "))
    min_mentions = int(input("What should be the minimum number of times a channel is mentioned to be included" 
                             " (5 recommended)? Enter number: "))

    max_posts_input = input("Enter max number of posts to check per channel (leave blank for no limit): ")
    max_posts = int(max_posts_input) if max_posts_input.strip() else None

    start_time = time.time()

    results = await process_channels(client, initial_channels, iterations, min_mentions, max_posts)
    await client.disconnect()

    print("Making CSV...")

    try:
        # Writing results to CSV
        with open('snowball_sampler_results.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            header = [f'Iteration {i}_id, Iteration {i}_channelname' for i in range(len(results))]
            writer.writerow([item for sublist in header for item in sublist.split(', ')])

            max_length = max(len(iteration) for iteration in results)
            for i in range(max_length):
                row = []
                for iteration in results:
                    if i < len(iteration):
                        row.extend(iteration[i])
                    else:
                        row.extend(['', ''])  # Empty strings for missing data
                writer.writerow(row)

    except IOError as e:
        print(f"IOError occurred: {e}")
        error_fix(results)
    except ValueError as e:
        print(f"ValueError occurred: {e}")
        error_fix(results)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        error_fix(results)

    end_time = time.time()
    total_time = end_time - start_time
    print(f"Total execution time: {total_time} seconds")

if __name__ == '__main__':
    # Running the main function in an event loop
    asyncio.run(main())